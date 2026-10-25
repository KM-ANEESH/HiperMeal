import base64
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.error import HTTPError
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server as s

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.db_patch = patch.object(s, 'DB', Path(self.temp.name) / 'test.sqlite3')
        self.db_patch.start()
        self.env = patch.dict(os.environ, {'HIPERMEAL_API_TOKEN': '', 'GEMINI_API_KEY': ''})
        self.env.start()
    def tearDown(self):
        self.db_patch.stop(); self.env.stop(); self.temp.cleanup()
    def payload(self):
        return {'date': '2026-10-25', 'title': 'Lunch', 'confirmed': True, 'items': [{'food_id':'rice','grams':150}]}
    def test_scaling_and_custom(self):
        result=s.estimate(self.payload())
        self.assertEqual(result['totals']['kcal'],195)
        self.assertEqual(result['totals']['protein'],4.05)
        result=s.estimate({'items':[{'name':'Label food','grams':50,'per_100g':{'kcal':200,'protein':10,'carbs':20,'fat':5}}]})
        self.assertEqual(result['totals']['kcal'],100)
    def test_invalid_portions_and_unknown_food(self):
        for value in [-1,0,float('nan'),float('inf'),True,'100',5001]:
            p=self.payload();p['items'][0]['grams']=value
            with self.assertRaises(s.ApiError):s.estimate(p)
        with self.assertRaises(s.ApiError):s.estimate({'items':[{'food_id':'imaginary','grams':100}]})
    def test_diary_lifecycle_persistence_and_totals(self):
        code, meal=s.route('POST','/api/meals',{},self.payload())
        self.assertEqual(code,201)
        path='/api/meals/'+meal['id']
        self.assertEqual(s.route('GET',path,{}, {})[1]['title'],'Lunch')
        p=self.payload();p['items'][0]['grams']=200
        s.route('PUT',path,{},p)
        self.assertEqual(s.route('GET','/api/summary',{'date':['2026-10-25']},{})[1]['totals']['kcal'],260)
        self.assertEqual(s.route('GET','/api/export',{}, {})[1]['count'],1)
        s.route('DELETE',path,{}, {})
        self.assertEqual(s.route('GET','/api/meals',{}, {})[1]['count'],0)
        with self.assertRaises(s.ApiError):s.route('GET',path,{}, {})
    def test_confirmation_and_date_required(self):
        p=self.payload();p['confirmed']=False
        with self.assertRaises(s.ApiError):s.meal_body(p)
        p=self.payload();p['date']='2026-02-30'
        with self.assertRaises(s.ApiError):s.meal_body(p)
    def test_missing_provider_and_consent(self):
        for p in [{},{'allow_cloud':True,'image_base64':'abc'}]:
            with self.assertRaises(s.ApiError):s.analyze(p)
    def test_image_provider_contract_and_invalid_image(self):
        image=io.BytesIO();s.Image.new('RGB',(8,8)).save(image,format='PNG')
        reply={'description':'A plate of rice','foods':[{'name':'rice','confidence':'medium','suggested_grams':150}], 'uncertainties':['Portion is uncertain']}
        upstream={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(reply)}]}}]}
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test-key'}),patch.object(s,'remote_json',return_value=upstream) as remote:
            result=s.analyze({'allow_cloud':True,'image_base64':base64.b64encode(image.getvalue()).decode()})
            self.assertTrue(result['requires_review']);self.assertFalse(result['photo_stored'])
            self.assertEqual(remote.call_count,1)
            with self.assertRaises(s.ApiError):s.analyze({'allow_cloud':True,'image_base64':'not an image'})
            upstream['candidates'][0]['finishReason']='MAX_TOKENS'
            with self.assertRaises(s.ApiError):s.analyze({'allow_cloud':True,'image_base64':base64.b64encode(image.getvalue()).decode()})
    def test_barcode_missing_values_not_zero(self):
        with patch.object(s,'remote_json',return_value={'status':1,'product':{'product_name':'Test','nutriments':{'energy-kj_100g':418.4}}}):
            result=s.barcode('12345678')
            self.assertAlmostEqual(result['per_100g']['kcal'],100)
            self.assertIsNone(result['per_100g']['protein']);self.assertFalse(result['complete'])
    def test_http_validation_auth_and_origin(self):
        http=s.ThreadingHTTPServer(('127.0.0.1',0),s.Handler)
        thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
        root=f'http://127.0.0.1:{http.server_port}'
        try:
            with urlopen(root+'/api/health') as response:self.assertEqual(response.status,200)
            for headers,body,status in [({'Content-Type':'application/json'},b'{',400),({'Content-Type':'text/plain'},b'{}',415),({'Content-Type':'application/json','Origin':'https://evil.example'},b'{}',403)]:
                with self.assertRaises(HTTPError) as error:urlopen(Request(root+'/api/estimate',data=body,headers=headers))
                self.assertEqual(error.exception.code,status)
            with patch.dict(os.environ,{'HIPERMEAL_API_TOKEN':'private-test'}):
                with self.assertRaises(HTTPError) as error:urlopen(root+'/api/meals')
                self.assertEqual(error.exception.code,401)
                with urlopen(Request(root+'/api/meals',headers={'Authorization':'Bearer private-test'})) as response:self.assertEqual(response.status,200)
        finally:http.shutdown();http.server_close();thread.join()

if __name__=='__main__':unittest.main()

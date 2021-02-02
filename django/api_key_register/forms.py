from django import forms

from setup_apikey.models  import  APIKEY

class  ApiKeyForm (forms.ModelForm):


    class Meta():
            model = APIKEY 
            fields = ('name','own_name','ex_id','api_keys','secret_keys','passphrase','exclude_pnl','added_by','tags')     # you can change the tuple element position to show it diffrently.
            
            labels = {   
                                                           #below label  is for changing labes as showin in forms
                'name': 'Name',
                'own_name':'own_name',
                'ex_id': 'Exchange_name',
                'api_keys': 'APIKEY',
                'secret_keys': 'Secrete Key',
                'passphrase': 'Pass Phrase',

                'exclude_pnl':'exclude_pnl',
                'added_by':'added_by',
                'tags':'tags',             
                
            }
  
    def __init__(self,*args, **kwargs):
        super(ApiKeyForm,self).__init__(*args, **kwargs)
         #below code is for not showing a empty label
        #self.fields['own_name'].empty_label = "select"
         #below code is for not showing a mandatory field
        #self.fields['emp_code'].required = False
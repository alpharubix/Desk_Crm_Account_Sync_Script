from os import write

from apscheduler.schedulers.background import BackgroundScheduler
import requests
import dotenv
import os

from access_token import AccessToken

dotenv.load_dotenv(override=True)

def get_all_accounts(token):
    total_desk_accounts = list()
    for index in range(1,6200,100):
          print(index)
          url =  f"https://desk.zoho.com/api/v1/accounts?from={index}&limit=100"
          headers = {
              'Authorization': f'Zoho-oauthtoken {token}'
          }
          try:
            response = requests.get(url,headers=headers)
            if response.status_code == 200:
              data = response.json().get('data')
              total_desk_accounts.append(data)
            elif response.status_code == 204:
                 print("ALL ACCOUNTS FETCHED SUCCESSFULLY")
          except requests.exceptions.RequestException as e:
              return e
          except requests.exceptions.HTTPError as e:
              print(e)
              return e
    return total_desk_accounts


def get_desk_account_with_ownerid(access_token,account_id):

    url = f'https://desk.zoho.com/api/v1/accounts/{account_id}?include=owner'
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'orgId': os.getenv('ORG_ID')
    }
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            data = response.json().get('owner','')
            return data
        else:
            print(response.status_code,response.text)
    except requests.exceptions.RequestException as e:
        return e

def get_crm_account_owner(access_token,crm_account_id):
    url = f'https://www.zohoapis.com/crm/v2/Accounts/{crm_account_id}'
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
    }
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            data = response.json().get('data')[0].get('Owner')
            return data
        else:
            print(response.status_code,response.text)
    except requests.exceptions.RequestException as e:
        print(e)
        return e


def mapping_initiator(access_token,desk_accounts):#initiator function which handles the checking and mapping logic
    owner_id_dict = {
        'Amare  Gowda': '666329000003245383',
        'Subhasini T S': '666329000000724001',
        'Namrata Srivastava': '666329000003200001',
        'Ayush Dingane': '666329000003245307',
        'Anslem Prathap': '666329000000139001',
        'Digamber Pandey': '666329000003244001',
        'Pallavi Gattu': '666329000003245421',
        'Honnappa Dinni': '666329000003245345',
        'Sandip Kumar Jena': '666329000003202001',
        'Sonu Sathyan': '666329000000804001',
        'Sutapa Roy B': '666329000003193001',
        'Kavya KB': '666329000003245117'}
    no_of_accounts_not_updated =0
    no_of_accounts_updated = 0
    no_of_unsynced_accounts = 0
    no_of_synced_accounts = 0
    access_token.generate_token_for_desk()
    access_token.generate_access_token_for_crm()
    scheduler = BackgroundScheduler()
    scheduler.add_job(access_token.generate_token_for_desk,trigger='interval',minutes=30)
    scheduler.add_job(access_token.generate_access_token_for_crm,trigger='interval',minutes=30)
    scheduler.start()
    page = 1
    for accounts in desk_accounts:
        print("page->",page)
        page = page + 1
        for acc in accounts:
           desk_acc_id = acc.get('id')
            #get the owner_id of that particular account
           account_owner = get_desk_account_with_ownerid(access_token.desk_access_token,desk_acc_id)
           if account_owner is None:
               print("Desk Account owner Not Found continue")
               with open("report.txt","a") as file:
                  file.write(f"Desk Account owner Not Found->{acc.get('accountName','No name found')}\n")
               continue
           desk_owner_name = ''.join(account_owner.get('firstName')+' '+account_owner.get('lastName'))
           print("Desk owner name->",desk_owner_name)
           crm_account_id = acc.get('zohoCRMAccount')
           if crm_account_id is not None and crm_account_id!= '':#which means only accounts with is synced will be mapped
              crm_owner_name =  get_crm_account_owner(access_token.crm_access_token,crm_account_id.get('id')).get('name')
              print("Crm owner name->",crm_owner_name)
              owner_id = owner_id_dict.get(crm_owner_name,'')
              print("mapped owner ID->",owner_id)
              if owner_id != '' and owner_id is not None :
                  if crm_owner_name != desk_owner_name.strip() :
                     #update the account with proper owner_id
                    update_result = update_desk_accounts(access_token.desk_access_token,desk_acc_id,owner_id)
                    print("updating the desk owner")
                    if update_result == 1:
                         no_of_accounts_updated+=1
                         print("Desk Account Owner Updated")
                  else:
                    print("Desk Account is already synced")
                    no_of_synced_accounts+=1
              else:
                    print("Desk Account failed owner id is equal or not found")
                    no_of_accounts_not_updated+=1
                    continue
           else:
               no_of_unsynced_accounts+=1
               with open("report.txt","a") as f:
                   f.write(acc.get('accountName','No name found'))
                   f.write('\n')
               print("desk account is not synced with the crm account")
    print("No_of_already-synced_account",no_of_synced_accounts)
    print("No_of_unsynced_account",no_of_unsynced_accounts)
    print("no_of_accounts_not_updated",no_of_accounts_not_updated)
    print("no_of_accounts_updated",no_of_accounts_updated)
    scheduler.shutdown(wait=False)

def update_desk_accounts(desk_token,desk_account_id,owner_id):
    url = f'https://desk.zoho.com/api/v1/accounts/{desk_account_id}'
    headers = {
        "Authorization": f'Zoho-oauthtoken {desk_token}',
        "orgId": os.getenv('org_id')
    }
    body = {
        "ownerId": owner_id,
    }
    try:
        response = requests.patch(url, headers=headers,json=body)
        print("update_result->",response.text)
        if response.status_code == 200:
            return 1
        else:
            return 0
    except requests.exceptions.RequestException as e:
        print("Expection occured at request at update function",e)
        return 0
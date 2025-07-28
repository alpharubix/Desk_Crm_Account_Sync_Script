import access_token
import owner_map
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    access_token_instance = access_token.AccessToken()
    desk_accounts = owner_map.get_all_accounts(access_token_instance.generate_token_for_desk().desk_access_token)
    initate = owner_map.mapping_initiator(access_token_instance,desk_accounts)





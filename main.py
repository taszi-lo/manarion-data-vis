from Manadata import ManaData

if __name__ == "__main__":

    ID = 69 # Put ID here.
    API = "abcd-1234-efgh-5678" # Put API here in quotation marks "".

    mana = ManaData(
        ID = ID,
        API = API,
    )

    # Display battler exp income.
    mana.vis_battlerexpincome()

    # Display dust income.
    mana.vis_dustincome()

    # Display taxed resources.
    mana.vis_taxed_resources()
    
    # Display investments.
    mana.vis_investments()
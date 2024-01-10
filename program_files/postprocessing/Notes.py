# get tech_flows (flows by which the processes of the calculated system are linked)
# bei einem System process gibt es logischerweise quasi keine
tech_flows = result.get_tech_flows()
print(
    pd.DataFrame(
        [
            (tf.provider.name, tf.flow.name, tf.flow.ref_unit)
            for tf in tech_flows
        ],
        columns=["Provider", "Flow", "Unit"],
    ).head()
)





############################INVENTORY######################

# TODO es gibt auch noch mehr get_envi_flows, mal prüfen ob ich das brauche
# ein part davon ist: get inventory
inventory = result.get_total_flows()
inventory_df = pd.DataFrame(
    data=[
        (
            i.envi_flow.flow.name,
            i.envi_flow.is_input,
            i.amount,
            i.envi_flow.flow.ref_unit,
        )
        for i in inventory
    ],
    columns=["Flow", "Is input?", "Amount", "Unit"],
)

# print an example of the table
print("Got Inventory")




#############ging eben noch#############

def calculate_results(product_system_ids):
    """
    Calculate the inventory of the system as well as the results of the impact assessment in one step
        :param product_system_ids
        :type list
    """

    # create empty dictionary for the impacts
    total_environmental_impacts = {}

    # Calculate the results for the electricity mix example
    for product_system in product_system_ids:

        setup = o.CalculationSetup(
            target=o.Ref(ref_type=o.RefType.ProductSystem, id=product_system),
            # unit automatically takes the unit of the quantitive reference
            impact_method=o.Ref(id="1f08b96a-0d3c-4e9e-88bf-09f2239f95e1"), # example: ReCiPe Midpoint H
            amount=10,  #hier später mit dem richtigen Amount verknüpfen,
            allocation=None,#keine allocation eingearbeit, lediglich von ProBas vordefiniert
                                # "amount of the reference flow of the calculation target for to which the result should be scaled"
            nw_set=None #kein normalization or weighting set
        )

        result = client.calculate(setup)
        result.wait_until_ready() #später hier noch n waiting print hinzufügen

        print(result)

        # get results for the impact categories
        impact_categories = result.get_total_impacts()

        # alternative
        total_impacts_df_new = pd.DataFrame(
            [(i.impact_category.name, i.amount)
             for i in impact_categories],
            columns=["Impact category", "Value"]
        )

        total_impacts_df_new = total_impacts_df_new.groupby("Impact category").sum().reset_index()

        print(total_impacts_df_new)

        # summarize the results for the different product systems over the impact categories
        for i in impact_categories:
            impact_category_name = i.impact_category.name
            if impact_category_name not in total_environmental_impacts:
                total_environmental_impacts[impact_category_name] = 0
            total_environmental_impacts[impact_category_name] += i.amount


    # Create the df (hier wird eigentlich nur aus dem dictionary nochmal ein df mit den richtigen überschriften gebildet
    total_impacts_df = pd.DataFrame(
        [(impact_category, total_value)
            for impact_category, total_value in total_environmental_impacts.items()],
        columns=["Impact category", "Total Value"],)

    print("Total impacts")
    print(total_impacts_df)

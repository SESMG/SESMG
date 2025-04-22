def build_input_dict(mode: str, input_data: dict) -> dict:
    input_values_dict = {}

    if mode == "advanced":
        input_values_dict["input_name"] = input_data.get("name", "")
        input_values_dict["input_pv"] = input_data.get("pv", 0)
        input_values_dict["input_st"] = input_data.get("st", 0)
        input_values_dict["input_ashp"] = input_data.get("ashp", 0)
        input_values_dict["input_gchp"] = input_data.get("gchp", 0)
        input_values_dict["input_battery"] = input_data.get("battery", 0)
        input_values_dict["input_dcts"] = input_data.get("dcts", 0)
        input_values_dict["input_chp"] = input_data.get("chp", 0)

        dh = input_data.get("dh", "No District Heating Network")
        if dh == "urban":
            input_values_dict.update({
                "input_chp_urban": 0, 
                "input_dh_urban": 1,
                "input_chp_sub_urban": 0, 
                "input_dh_sub_urban": 0,
                "input_chp_rural": 0, 
                "input_dh_rural": 0,
                "input_chp_a": 1
            })
        elif dh == "sub-urban":
            input_values_dict.update({
                "input_chp_urban": 0, 
                "input_dh_urban": 1,
                "input_chp_sub_urban": 0, 
                "input_dh_sub_urban": 1,
                "input_chp_rural": 0, 
                "input_dh_rural": 0,
                "input_chp_a": 1
            })
        elif dh == "rural":
            input_values_dict.update({
                "input_chp_urban": 0, 
                "input_dh_urban": 1,
                "input_chp_sub_urban": 0, 
                "input_dh_sub_urban": 1,
                "input_chp_rural": 0, 
                "input_dh_rural": 1,
                "input_chp_a": 1
            })
        else:
            input_values_dict.update({
                "input_chp_urban": 0, 
                "input_dh_urban": 0,
                "input_chp_sub_urban": 0,
                "input_dh_sub_urban": 0,
                "input_chp_rural": 0, 
                "input_dh_rural": 0,
                "input_chp_a": 1
            })

        input_values_dict["solver_select"] = input_data.get("solver", "cbc")
        input_values_dict["input_criterion"] = input_data.get("criterion", "monetary")

    else:  # simplified
        def percent(val, total): return int(val * total)
        input_values_dict["input_name"] = input_data.get("name", "")
        input_values_dict["input_pv"] = percent(input_data.get("pv", 0), 10000)
        input_values_dict["input_st"] = percent(input_data.get("st", 0), 27700)
        input_values_dict["input_ashp"] = percent(input_data.get("ashp", 0), 5000)
        input_values_dict["input_gchp"] = percent(input_data.get("gchp", 0), 5000)
        input_values_dict["input_battery"] = percent(input_data.get("battery", 0), 10000)
        input_values_dict["input_dcts"] = percent(input_data.get("dcts", 0), 10000)
        input_values_dict["input_chp"] = 0

        dh = input_data.get("dh", "No District Heating Network")
        if dh == "urban":
            input_values_dict.update({
                "input_chp_urban": 1, 
                "input_dh_urban": 1,
                "input_chp_sub_urban": 0, 
                "input_dh_sub_urban": 0,
                "input_chp_rural": 0, 
                "input_dh_rural": 0,
                "input_chp_a": 0
            })
        elif dh == "sub-urban":
            input_values_dict.update({
                "input_chp_urban": 1, 
                "input_dh_urban": 1,
                "input_chp_sub_urban": 1, 
                "input_dh_sub_urban": 1,
                "input_chp_rural": 0, 
                "input_dh_rural": 0,
                "input_chp_a": 0
            })
        elif dh == "rural":
            input_values_dict.update({
                "input_chp_urban": 1, 
                "input_dh_urban": 1,
                "input_chp_sub_urban": 1, 
                "input_dh_sub_urban": 1,
                "input_chp_rural": 1, 
                "input_dh_rural": 1,
                "input_chp_a": 0
            })
        else:
            input_values_dict.update({
                "input_chp_urban": 0, 
                "input_dh_urban": 0,
                "input_chp_sub_urban": 0, 
                "input_dh_sub_urban": 0,
                "input_chp_rural": 0, 
                "input_dh_rural": 0,
                "input_chp_a": 0
            })

        input_values_dict["solver_select"] = input_data.get("solver", "cbc")
        input_values_dict["input_criterion"] = input_data.get("criterion", "monetary")

    return input_values_dict

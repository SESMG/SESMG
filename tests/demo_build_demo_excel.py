import os
def build_demo_excel(input_dict, template_path, save_path, set_cell_func, execute_func):
    """
    Creates a modified Excel file from a template, using dummy input values.

    :param input_dict: dictionary with input values
    :param template_path: path to the original template file
    :param save_path: path where to save the new file
    :param set_cell_func: function to modify a cell (mocketable)
    :param execute_func: function to execute the template (mockeable)
    """

    import openpyxl

    xfile = openpyxl.load_workbook(template_path, data_only=True)

    # PV
    set_cell_func(xfile, "Photo1", input_dict["input_pv"])
    set_cell_func(xfile, "Photo2", input_dict["input_pv"])

    # Solar Thermal
    set_cell_func(xfile, "Solart1", input_dict["input_st"])
    set_cell_func(xfile, "Solart2", input_dict["input_st"])

    # Battery
    set_cell_func(xfile, "Battery1", input_dict["input_battery"])
    set_cell_func(xfile, "Battery2", input_dict["input_battery"])

    # Thermal Storage
    set_cell_func(xfile, "DCTS1", input_dict["input_dcts"])
    set_cell_func(xfile, "DCTS2", input_dict["input_dcts"])

    # GCHP
    set_cell_func(xfile, "GCHP1", input_dict["input_gchp"])
    set_cell_func(xfile, "GCHP2", input_dict["input_gchp"])

    # ASHP
    set_cell_func(xfile, "ASHP1", input_dict["input_ashp"])
    set_cell_func(xfile, "ASHP2", input_dict["input_ashp"])

    # CHP
    set_cell_func(xfile, "CHPtr1", input_dict["input_chp"])
    set_cell_func(xfile, "CHPtr2", input_dict["input_chp"])

    # District Heating
    set_cell_func(xfile, "dhurban", input_dict["input_dh_urban"])
    set_cell_func(xfile, "dhsuburban", input_dict["input_dh_sub_urban"])
    set_cell_func(xfile, "dhrural", input_dict["input_dh_rural"])

    set_cell_func(xfile, "chpurban", input_dict["input_chp_urban"])
    set_cell_func(xfile, "chpsuburban", input_dict["input_chp_sub_urban"])
    set_cell_func(xfile, "chprural", input_dict["input_chp_rural"])
    set_cell_func(xfile, "chpa", input_dict["input_chp_a"])

    # Save file
    xfile.save(save_path)

    # Execute end function
    execute_func(
        demo_file=save_path,
        demo_results=os.path.dirname(save_path),
        mode=input_dict["input_criterion"]
    )

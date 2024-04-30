import pandas


def test_get_dict_building_cluster():
    """
        Test if the extraction of the necessary data for a cluster
        works.
    """
    from program_files.urban_district_upscaling.clustering \
        import get_dict_building_cluster
    
    # create input Dataframe
    tool = pandas.DataFrame.from_dict(
        {"active": [1, 1, 1],
         "label": ["test1", "test2", "test3"],
         "parcel ID":  ["test1", "test2", "test3"],
         "building type": ["single family building",
                           "multi family building",
                           "commercial food"],
         "cluster ID": ["test1", "test1", "test2"]})
    # create expected output dictionary
    test_cluster_ids = {"test1": [["test1", "test1", "single family building"],
                                  ["test2", "test2", "multi family building"]],
                        "test2": [["test3", "test3", "commercial food"]]}
    # start method to be tested
    cluster_ids, building_labels = get_dict_building_cluster(tool)
    # check rather the two dicts are the same
    assert test_cluster_ids == cluster_ids
    assert building_labels == ["test1", "test2", "test3"]

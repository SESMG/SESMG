# TODO decide whether include MAX PV and MAX ST or the percentage of area usage ??
# todo 2021-11-02: Bei max PV/ST starten

import pandas as pd
import os


# TODO find another way to get the combination of cluster and building id
label_Cluster = {
    "L10000roA": "116",
    "L10000rob": "79",
    "L10000rrr": "66",
    "L10000rsu": "112",
    "L10000rUV": "135",
    "L10000rwG": "224",
    "L10000rXw": "272",
    "L10000rZO": "227",
    "L10000sF9": "129",
    "L10000s6c": "30",
    "L10000s6e": "116",
    "L10000uf7": "129",
    "L10000sY4": "51",
    "L10000sZ7": "253",
    "L10000tE5": "158",
    "L10000uaC": "265",
    "L10000ubf": "215",
    "L10000uBM": "265",
    "L10000uBt": "216",
    "L10000uBx": "216",
    "L10000uiJ": "129",
    "L10000uCa": "53",
    "L10000uCc": "64",
    "L10000uDK": "156",
    "L10000uDk": "53",
    "L10000uDQ": "265",
    "L10000uDu": "224",
    "L10000uDW": "66",
    "L10000uDY": "46",
    "L10000uDy": "46",
    "L10000uEB": "262",
    "L10000uen": "91",
    "L10000uL5": "129",
    "L10000uF0": "110",
    "L10000urB": "129",
    "L10000uvo": "129",
    "L10000ufK": "121",
    "L10000uFK": "280",
    "L10000uFn": "53",
    "L10000vaP": "129",
    "L10000ufS": "265",
    "L10000ugh": "224",
    "L10000uGj": "265",
    "L10000vb0": "129",
    "L10000uGn": "110",
    "L10000uGO": "156",
    "L10000uGQ": "121",
    "L10000vln": "129",
    "L10000uH5": "215",
    "L10000uHD": "173",
    "L10000uHQ": "91",
    "L10000uhr": "79",
    "L10000uHS": "215",
    "L10000uhz": "64",
    "L10000ui1": "139",
    "L10000vow": "129",
    "L10000ui7": "110",
    "L10000uI8": "291",
    "L10000uIb": "233",
    "L10000vpI": "129",
    "L10000vPL": "129",
    "L10000uIk": "262",
    "L10000uIR": "291",
    "L10000vQH": "129",
    "L10000uiv": "266",
    "L10000uJA": "215",
    "L10000ujd": "265",
    "L10000uJf": "291",
    "L10000vUv": "129",
    "L10000uJK": "79",
    "L10000uJY": "53",
    "L10000uKA": "64",
    "L10000ukG": "224",
    "L10000ukh": "2",
    "L10000uKN": "291",
    "L10000uKP": "270",
    "L10000ukt": "201",
    "L10000uL3": "151",
    "L10000vvi": "129",
    "L10000ulV": "79",
    "L10000um0": "110",
    "L10000vvn": "129",
    "L10000uM7": "215",
    "L10000umF": "64",
    "L10000umL": "83",
    "L10000umm": "291",
    "L10000umP": "224",
    "L10000umx": "156",
    "L10000unh": "265",
    "L10000uNJ": "53",
    "L10000w6f": "129",
    "L10000uNW": "64",
    "L10000uo1": "141",
    "L10000uoa": "91",
    "L10000uOG": "270",
    "L10000uoK": "11",
    "L10000uOq": "53",
    "L10000w7Q": "129",
    "L10000uPC": "262",
    "L10000upC": "291",
    "L10000upk": "265",
    "L10000upm": "46",
    "L10000upo": "201",
    "L10000upU": "224",
    "L10000uq7": "291",
    "L10000uqa": "48",
    "L10000wDK": "129",
    "L10000uqI": "79",
    "L10000uQl": "79",
    "L10000uQr": "48",
    "L10000uQx": "291",
    "L10000uqz": "270",
    "L10000ur9": "265",
    "L10000uRA": "53",
    "L10000wfe": "129",
    "L10000uRE": "64",
    "L10000urJ": "127",
    "L10000urP": "79",
    "L10000uru": "270",
    "L10000urV": "291",
    "L10000urw": "224",
    "L10000urX": "291",
    "L10000usL": "48",
    "L10000usm": "64",
    "L10000usq": "11",
    "L10000utU": "262",
    "L10000uTX": "25",
    "L10000uU2": "291",
    "L10000uu8": "11",
    "L10000uua": "270",
    "L10000uuc": "46",
    "L10000uuQ": "110",
    "L10000uUQ": "262",
    "L10000uUS": "14",
    "L10000uv1": "262",
    "L10000wFS": "129",
    "L10000uVZ": "265",
    "L10000uw0": "53",
    "L10000wgD": "129",
    "L10000uwM": "79",
    "L10000win": "129",
    "L10000uwt": "262",
    "L10000uXH": "158",
    "L10000wJg": "129",
    "L10000uYv": "30",
    "L10000uzl": "270",
    "L10001NbI": "129",
    "L10000v0i": "270",
    "L10000v1A": "64",
    "L10000v1e": "291",
    "L10001Ncr": "129",
    "L10000v1z": "79",
    "L10000v27": "270",
    "L10000v2K": "270",
    "L10000v2o": "212",
    "L10000v2U": "224",
    "L10001NdQ": "129",
    "L10000v3b": "291",
    "L10000v3G": "11",
    "L10000v3R": "291",
    "L10000v41": "64",
    "L10001NHE": "129",
    "L10000v57": "48",
    "L10000v5a": "270",
    "L10000v5J": "64",
    "L10000v5V": "53",
    "L10001NKH": "129",
    "L10000v6B": "224",
    "L10000v6D": "291",
    "L10000v6P": "42",
    "L10000v7e": "201",
    "L10000v7T": "42",
    "L10001NSq": "129",
    "L10000v8y": "270",
    "L10000v93": "265",
    "L10000v9D": "270",
    "L10000v9d": "270",
    "L10000v9o": "66",
    "L10001NVT": "129",
    "L10000vAE": "262",
    "L10000vaf": "42",
    "L10000vaj": "46",
    "L10000vaL": "201",
    "L10000van": "64",
    "L10001NZR": "129",
    "L10000vas": "46",
    "L10001NZz": "129",
    "L10000vau": "270",
    "L10000vaw": "270",
    "L10000vAZ": "64",
    "L10008IJy": "129",
    "L10000vba": "11",
    "L10000vbA": "270",
    "L10008IK3": "129",
    "L10000vBO": "224",
    "L10008IK8": "129",
    "L10000vc1": "201",
    "L10000vCc": "110",
    "L10000vcH": "291",
    "L10000vCm": "216",
    "L10000vcN": "48",
    "L10000vCs": "48",
    "L10000vCu": "262",
    "L10000vDG": "201",
    "L10000vDK": "291",
    "L10000vDO": "121",
    "L10000vds": "48",
    "L10000vE9": "265",
    "L10000vEF": "53",
    "L10000veh": "224",
    "L10000vfC": "42",
    "L10000vfQ": "270",
    "L10000vFt": "201",
    "L10000vFU": "79",
    "L10000vgA": "270",
    "L10000vgd": "11",
    "L10000vGE": "66",
    "L10000vgf": "265",
    "L10000vgG": "265",
    "L10008IKD": "129",
    "L10000vgk": "64",
    "L10000vgS": "53",
    "L10000vGS": "53",
    "L10008IKS": "129",
    "L10000vHB": "201",
    "L10000vhC": "270",
    "L10000vhI": "262",
    "L10008IL5": "129",
    "L10008ILA": "129",
    "L10000vHW": "291",
    "L10000vhY": "262",
    "L10008ILF": "129",
    "L10000vi3": "224",
    "L10000vIB": "274",
    "L10000viC": "53",
    "L10000vIH": "262",
    "L10000vIo": "216",
    "L10000vJ6": "42",
    "L10000vjn": "262",
    "L10000vJq": "291",
    "L10000vju": "46",
    "L10000vK2": "201",
    "L10008ILM": "129",
    "L10000vk8": "48",
    "L10000vK8": "53",
    "L10000vka": "224",
    "L10000vKb": "46",
    "L10000vKC": "53",
    "L10000vkc": "224",
    "L10000vkr": "34",
    "L10000vL0": "48",
    "L10000vL5": "46",
    "L10000vlG": "53",
    "L10000vlh": "270",
    "L10008l4e": "129",
    "L10000vlt": "262",
    "L10000vmH": "229",
    "L10000vMP": "46",
    "L10000vMR": "280",
    "L10000vmv": "42",
    "L10000vNa": "216",
    "L10000vNM": "201",
    "L10000vNn": "79",
    "L10000vo3": "66",
    "L10000vO8": "156",
    "L10000vOO": "262",
    "L10000vou": "262",
    "L10008l51": "129",
    "L10000vOZ": "57",
    "L10008l5E": "129",
    "L10000vP6": "79",
    "L10000vpa": "216",
    "L10000vpf": "262",
    "L10000vpG": "233",
    "L10008l5K": "129",
    "L10000vPJ": "11",
    "L10008TJi": "129",
    "L10000vpr": "224",
    "L10000vpu": "201",
    "L10000vpW": "11",
    "L10000vQ9": "265",
    "L10000vQa": "262",
    "L10000vQB": "64",
    "L10000vqb": "110",
    "L10000vQg": "270",
    "L10008TJR": "129",
    "L10008TJX": "129",
    "L10000vqz": "270",
    "L10000vR6": "262",
    "L10000vRA": "42",
    "L10000vRH": "156",
    "L10000vRn": "46",
    "L10000vRs": "265",
    "L10000vrX": "201",
    "L10000vs0": "53",
    "L10000vS6": "291",
    "L10000vs7": "53",
    "L10000vSD": "141",
    "L10008Y8d": "129",
    "L10000vSw": "224",
    "L10000vsX": "291",
    "L10000vsy": "11",
    "L10000vSy": "265",
    "L10000vt2": "291",
    "L10000vtA": "139",
    "L10000vtg": "53",
    "L10000vtn": "224",
    "L10008Y8E": "129",
    "L10000vu1": "291",
    "L10000vUd": "291",
    "L10008Y8G": "129",
    "L10008Y8L": "129",
    "L10008Y8n": "129",
    "L10000vUP": "64",
    "L10008Y8T": "129",
    "L1000918f": "129",
    "L10000vVB": "64",
    "L10000vvc": "42",
    "L10000vvF": "42",
    "L1000918j": "129",
    "L10000vVj": "270",
    "L1000918m": "129",
    "L10000vVV": "79",
    "L10000vvv": "291",
    "L1000918p": "129",
    "L10000vWk": "64",
    "L10000vwK": "291",
    "L10000vWL": "48",
    "L10000vWR": "53",
    "L10000vWT": "216",
    "L22000004": "129",
    "L2P00005d": "129",
    "L2P00005r": "129",
    "L10000vxF": "270",
    "L10000vXm": "121",
    "L10000vxr": "201",
    "LF00000N9": "129",
    "L10000vxU": "64",
    "L10000vXw": "291",
    "L10000vXX": "201",
    "L10000vyB": "265",
    "LF00000NE": "129",
    "L10000vYh": "64",
    "L10000vYl": "265",
    "L10000vyp": "53",
    "L10000vYr": "53",
    "L10000vyr": "224",
    "L10000vYy": "53",
    "L10000vZp": "53",
    "L10000w0Z": "262",
    "L10000w1F": "110",
    "L10000w2e": "53",
    "L10000w2r": "224",
    "L10000w3M": "233",
    "L10000w3x": "91",
    "L10000w4B": "46",
    "L10000w4j": "264",
    "L10000w4r": "48",
    "LF00000NH": "129",
    "L10000w5j": "291",
    "LF00000NN": "129",
    "LF00000NS": "129",
    "L10000w6n": "26",
    "L10000w6Z": "215",
    "L10000w72": "91",
    "L10000w7C": "270",
    "L10000w7M": "274",
    "LF00000NV": "129",
    "L10000w7Y": "291",
    "L10000w8B": "262",
    "L10000w8q": "233",
    "L10000w8R": "224",
    "L10000w8u": "57",
    "L10000w8y": "262",
    "L10000w90": "265",
    "L10000w92": "216",
    "L10000w9C": "215",
    "L10000w9e": "262",
    "LF00000Nz": "129",
    "L10000wA2": "110",
    "L10000wA8": "11",
    "L10000wAb": "53",
    "LF00000O8": "129",
    "L10000wAj": "91",
    "L10000wAp": "224",
    "L10000wAT": "233",
    "L10000wAV": "201",
    "L10000wAx": "291",
    "L10000wBA": "64",
    "L10000wBf": "224",
    "L10000wBr": "79",
    "L10000wBV": "158",
    "L10000wC1": "224",
    "L10000wD2": "201",
    "L10000wd5": "5",
    "L10000wD6": "257",
    "L10000wDC": "64",
    "L10000wDE": "224",
    "L10000wDI": "224",
    "LF00000Om": "129",
    "L10000wDM": "48",
    "L10000wDt": "42",
    "L10000wDV": "215",
    "L10000wdx": "79",
    "L10000wE7": "117",
    "L10000weM": "224",
    "L10000wER": "64",
    "L10000weU": "262",
    "LF00000OZ": "129",
    "LF00000P3": "129",
    "L10000wFQ": "262",
    "LF00000P6": "129",
    "L10000wGD": "201",
    "LF00000P7": "129",
    "L10000wgf": "262",
    "LF00000PA": "129",
    "L10000wgs": "201",
    "L10000wgu": "11",
    "L10000wh7": "79",
    "L10000whc": "121",
    "L10000wHl": "110",
    "L10000whY": "216",
    "L10000wi2": "79",
    "L10000wiK": "64",
    "LF00000Pc": "129",
    "L10000wIn": "262",
    "L10000wIS": "53",
    "L10000wiT": "270",
    "L10000wiV": "270",
    "L10000wJC": "53",
    "LF00000PD": "129",
    "L10000wjH": "156",
    "L10000wjv": "262",
    "L10000wJy": "262",
    "L10000wOW": "270",
    "L10000wRV": "64",
    "L10000wRX": "46",
    "L10000xvL": "135",
    "L10000xy6": "233",
    "L10000xyG": "274",
    "L10000y0J": "11",
    "L10000y1C": "11",
    "L10001N5c": "265",
    "L10001N5d": "265",
    "L10001N5e": "30",
    "L10001N5m": "224",
    "L10001N5p": "233",
    "L10001N5S": "270",
    "L10001N5t": "265",
    "L10001N5v": "79",
    "L10001N5w": "15",
    "LF00000Pg": "129",
    "LF00000PG": "129",
    "L10001N62": "151",
    "L10001N6C": "270",
    "L10001N6f": "215",
    "L10001N6j": "262",
    "L10001N6K": "91",
    "L10001N6p": "79",
    "L10001N6R": "224",
    "L10001N6v": "206",
    "L10001N6Y": "15",
    "L10001N6y": "46",
    "L10001N70": "64",
    "L10001N77": "265",
    "L10001N79": "83",
    "L10001N7d": "46",
    "L10001N7g": "270",
    "L10001N7h": "270",
    "L10001N7m": "270",
    "L10001N7N": "174",
    "L10001N7o": "109",
    "L10001N7p": "270",
    "L10001N7s": "11",
    "L10001N7t": "79",
    "L10001N7V": "206",
    "L10001N7X": "15",
    "LF00000PK": "129",
    "L10001N82": "206",
    "L10001N8F": "216",
    "L10001N8H": "15",
    "L10001N8L": "216",
    "L10001N8M": "137",
    "L10001N8s": "15",
    "L10001N8S": "262",
    "L10001N8u": "78",
    "L10001N8v": "53",
    "L10001N91": "83",
    "L10001N92": "110",
    "L10001N95": "291",
    "L10001N97": "224",
    "L10001N9B": "15",
    "L10001N9b": "265",
    "L10001N9G": "139",
    "L10001N9j": "265",
    "L10001N9L": "53",
    "L10001N9N": "137",
    "L10001N9R": "265",
    "LF00000Ps": "129",
    "L10001N9V": "47",
    "L10001N9y": "83",
    "L10001N9Z": "158",
    "L10001Na2": "174",
    "L10001NA2": "262",
    "L10001NA3": "46",
    "L10001Na4": "53",
    "L10001NA4": "237",
    "L10001NA7": "215",
    "L10001NAA": "135",
    "L10001NAB": "224",
    "L10001NAD": "216",
    "L10001Nae": "265",
    "L10001NAf": "173",
    "L10001Naf": "174",
    "L10001NaG": "117",
    "L10001NAi": "15",
    "L10001NAJ": "53",
    "L10001NAj": "53",
    "LS00000Fr": "129",
    "L10001NAM": "270",
    "L10001Nao": "64",
    "L10001NaQ": "139",
    "L10001NAR": "265",
    "L10001NAT": "25",
    "L10001NAt": "64",
    "L10001NaU": "265",
    "L10001NaV": "57",
    "L10001NAy": "15",
    "L10001NaY": "0",
    "L10001Nay": "262",
    "L10001NAZ": "64",
    "L10001Nb0": "53",
    "L10001NB2": "270",
    "L10001NB3": "2",
    "L10001Nb8": "271",
    "L10001NB8": "174",
    "L10001NB9": "15",
    "LS00000Fw": "129",
    "L10001NBa": "262",
    "L10001NbC": "291",
    "L10001Nbd": "262",
    "L10001NBe": "265",
    "L10001NBF": "224",
    "L10001NBf": "224",
    "L10001Nbg": "224",
    "L10001NBh": "206",
    "L10001Nbh": "270",
    "L10000uBY": "157",
    "L10001NBL": "11",
    "L10001NbL": "53",
    "L10000uER": "157",
    "L10001NBN": "265",
    "L10001NBR": "110",
    "L10001Nbr": "270",
    "L10000uF8": "157",
    "L10001Nbs": "233",
    "L10001NBu": "109",
    "L10001NbV": "265",
    "L10000uFr": "157",
    "L10001NBx": "224",
    "L10001NbZ": "265",
    "L10001NC0": "280",
    "L10000uGZ": "157",
    "L10001NC5": "224",
    "L10001Nc7": "79",
    "L10001NC8": "224",
    "L10001NcA": "53",
    "L10001NCA": "53",
    "L10001NCa": "291",
    "L10001NCB": "262",
    "L10001NCD": "262",
    "L10001NcD": "262",
    "L10001NCe": "265",
    "L10001NcE": "265",
    "L10001Ncf": "174",
    "L10001NCf": "262",
    "L10001NCH": "237",
    "L10001Ncj": "15",
    "L10000ui3": "157",
    "L10001NcL": "25",
    "L10001NCl": "265",
    "L10001Ncm": "229",
    "L10001NCM": "265",
    "L10001NCN": "79",
    "L10000uID": "157",
    "L10001NcS": "42",
    "L10001NCs": "265",
    "L10001NcU": "206",
    "L10001NCV": "224",
    "L10000uIv": "157",
    "L10001Ncw": "137",
    "L10000ujI": "157",
    "L10001Ncx": "224",
    "L10000uM3": "157",
    "L10000unr": "157",
    "L10001NCZ": "224",
    "L10000up5": "157",
    "L10001Nd5": "265",
    "L10001Nd7": "15",
    "L10001ND8": "265",
    "L10001Nd8": "224",
    "L10001ND9": "110",
    "L10001Nd9": "265",
    "L10001NdA": "265",
    "L10001NdB": "15",
    "L10001NDB": "46",
    "L10001Ndb": "42",
    "L10001Ndc": "64",
    "L10001NDC": "262",
    "L10001Ndd": "46",
    "L10001NDD": "270",
    "L10001NDe": "206",
    "L10001Nde": "270",
    "L10001NDF": "265",
    "L10001NdF": "265",
    "L10001NdG": "224",
    "L10000uQb": "157",
    "L10001NDJ": "262",
    "L10001NdK": "265",
    "L10001NDM": "53",
    "L10000uym": "157",
    "L10001Ndn": "83",
    "L10001Ndo": "137",
    "L10000uzs": "157",
    "L10000v1M": "157",
    "L10001NDR": "46",
    "L10001Ndr": "262",
    "L10001Ndt": "262",
    "L10001Ndu": "265",
    "L10001NDw": "53",
    "L10001Ndw": "224",
    "L10001NDX": "15",
    "L10001NDx": "265",
    "L10001NDY": "126",
    "L10001NdY": "262",
    "L10001Ne1": "271",
    "L10001NE1": "262",
    "L10000v2v": "157",
    "L10001NE4": "53",
    "L10001Ne8": "224",
    "L10001NEB": "262",
    "L10000v4l": "157",
    "L10001Neg": "15",
    "L10001NEI": "265",
    "L10001NeI": "224",
    "L10001NeJ": "224",
    "L10001NEj": "270",
    "L10001NEK": "15",
    "L10001Nel": "265",
    "L10001NeM": "15",
    "L10001Nep": "260",
    "L10001NEP": "272",
    "L10001NEQ": "224",
    "L10001Ner": "270",
    "L10001NES": "53",
    "L10001Nev": "110",
    "L10001New": "15",
    "L10001NEx": "206",
    "L10000v69": "157",
    "L10001NEz": "110",
    "L10000v8L": "157",
    "L10001NF3": "53",
    "L10001Nf5": "117",
    "L10001NF5": "216",
    "L10001NF7": "265",
    "L10000va5": "157",
    "L10000vaT": "157",
    "L10001Nfa": "270",
    "L10001NFb": "262",
    "L10001NFc": "265",
    "L10001NFD": "262",
    "L10001NfD": "262",
    "L10001NFe": "42",
    "L10001Nfe": "270",
    "L10001Nff": "212",
    "L10001NfH": "11",
    "L10001NFi": "46",
    "L10001NfI": "224",
    "L10001NFI": "272",
    "L10001NFJ": "117",
    "L10001NFj": "224",
    "L10001Nfj": "224",
    "L10001NfK": "109",
    "L10001NFK": "265",
    "L10001NfL": "15",
    "L10001NFM": "53",
    "L10000vbc": "157",
    "L10001NfN": "139",
    "L10001NFQ": "64",
    "L10001NFR": "64",
    "L10001NfR": "262",
    "L10001Nfs": "53",
    "L10001NFs": "224",
    "L10001NfU": "91",
    "L10001NFU": "291",
    "L10001NFV": "79",
    "L10001NFv": "138",
    "L10001Nfy": "53",
    "L10000vbv": "157",
    "L10001Ng0": "216",
    "L10001NG1": "224",
    "L10000vGI": "157",
    "L10001Ng5": "265",
    "L10001NG6": "224",
    "L10001Nga": "15",
    "L10001NGa": "265",
    "L10000vh2": "157",
    "L10001NGE": "53",
    "L10001NGf": "53",
    "L10000vHm": "157",
    "L10001NGJ": "64",
    "L10001NGk": "224",
    "L10001NGL": "15",
    "L10000vhw": "157",
    "L10001NGn": "265",
    "L10001NGO": "265",
    "L10001NGQ": "42",
    "L10001NgR": "91",
    "L10001NGS": "83",
    "L10001NGw": "31",
    "L10001NGX": "248",
    "L10001NH0": "15",
    "L10001NHd": "15",
    "L10001NHD": "215",
    "L10000vI1": "157",
    "L10000vk4": "157",
    "L10001NHf": "174",
    "L10001NHK": "265",
    "L10001NHn": "110",
    "L10001NHO": "42",
    "L10001NHQ": "57",
    "L10001NHR": "262",
    "L10001NHs": "265",
    "L10001NI3": "42",
    "L10001NI9": "64",
    "L10001NIB": "15",
    "L10001NIb": "64",
    "L10001NIE": "117",
    "L10001NIF": "265",
    "L10001NIj": "224",
    "L10001NIL": "216",
    "L10001NIp": "270",
    "L10001NIV": "291",
    "L10001NIW": "15",
    "L10001NIX": "53",
    "L10001NIx": "79",
    "L10001NJ0": "46",
    "L10001NJ1": "224",
    "L10001NJd": "91",
    "L10001NJf": "11",
    "L10001NJh": "265",
    "L10001NJI": "191",
    "L10001NJJ": "216",
    "L10001NJK": "31",
    "L10001NJO": "53",
    "L10001NK1": "206",
    "L10001NK2": "2",
    "L10001NK8": "216",
    "L10001NK9": "173",
    "L10001NKB": "262",
    "L10001NKc": "46",
    "L10000vOz": "157",
    "L10001NKj": "64",
    "L10001NKn": "270",
    "L10001NKu": "46",
    "L10001NKU": "110",
    "L10001NKw": "64",
    "L10001NKX": "15",
    "L10001NKy": "126",
    "L10001NKZ": "270",
    "L10001NL4": "291",
    "L10001NLA": "265",
    "L10001NLf": "206",
    "L10001NLg": "79",
    "L10001NLK": "224",
    "L10001NLn": "270",
    "L10001NLr": "15",
    "L10001NLs": "191",
    "L10001NLv": "79",
    "L10001NLV": "224",
    "L10001NLx": "109",
    "L10001NM0": "162",
    "L10001NM7": "53",
    "L10001NM8": "15",
    "L10001NMA": "15",
    "L10001NMd": "250",
    "L10001NMH": "15",
    "L10001NMj": "15",
    "L10001NMk": "271",
    "L10001NMP": "53",
    "L10001NMR": "270",
    "L10001NMy": "53",
    "L10001NNB": "216",
    "L10001NNC": "30",
    "L10001NNq": "64",
    "L10000vqY": "157",
    "L10001NO3": "262",
    "L10001NO8": "53",
    "L10001NOB": "265",
    "L10001NOb": "265",
    "L10001NOc": "270",
    "L10001NOJ": "265",
    "L10001NOn": "265",
    "L10001NOP": "91",
    "L10001NOq": "117",
    "L10001NOR": "224",
    "L10001NOU": "138",
    "L10001NOu": "224",
    "L10001NOV": "270",
    "L10001NOY": "212",
    "L10000vsT": "157",
    "L10001NPB": "64",
    "L10001NPb": "117",
    "L10001NPE": "53",
    "L10001NPf": "215",
    "L10001NPR": "110",
    "L10000vU1": "157",
    "L10001NPv": "121",
    "L10000vue": "157",
    "L10001NQ1": "64",
    "L10001NQ8": "31",
    "L10001NQd": "64",
    "L10001NQg": "265",
    "L10001NQH": "224",
    "L10001NQh": "262",
    "L10001NQj": "78",
    "L10001NQn": "15",
    "L10001NQN": "53",
    "L10001NQr": "42",
    "L10001NQW": "30",
    "L10001NQw": "265",
    "L10000vUH": "157",
    "L10001NR0": "53",
    "L10001NR8": "78",
    "L10001NR9": "15",
    "L10001NRe": "265",
    "L10001NRG": "64",
    "L10001NRh": "117",
    "L10001NRj": "265",
    "L10000vuJ": "157",
    "L10001NRl": "262",
    "L10001NRN": "270",
    "L10001NRR": "79",
    "L10001NRS": "53",
    "L10001NRY": "265",
    "L10000vUT": "157",
    "L10001NS5": "64",
    "L10001NS7": "0",
    "L10001NSd": "64",
    "L10001NSD": "237",
    "L10001NSG": "15",
    "L10001NSi": "250",
    "L10001NSm": "83",
    "L10001NSM": "270",
    "L10001NSn": "260",
    "L10000vW0": "157",
    "L10001NSR": "46",
    "L10001NSS": "224",
    "L10001NSV": "233",
    "L10001NSX": "11",
    "L10001NSy": "216",
    "L10001NSz": "53",
    "L10001NT1": "117",
    "L10001NT9": "265",
    "L10000vWz": "157",
    "L10001NTh": "15",
    "L10000vXA": "157",
    "L10001NTM": "15",
    "L10001NTm": "271",
    "L10001NTN": "30",
    "L10001NTO": "64",
    "L10001NTT": "291",
    "L10001NTu": "270",
    "L10001NTw": "224",
    "L10001NTX": "265",
    "L10001NTZ": "2",
    "L10001NU0": "216",
    "L10001NU2": "224",
    "L10001NU3": "265",
    "L10001NU5": "224",
    "L10001NUc": "262",
    "L10001NUN": "291",
    "L10001NUO": "224",
    "L10001NUP": "224",
    "L10001NUq": "265",
    "L10001NUZ": "46",
    "L10001NV5": "233",
    "L10001NVC": "204",
    "L10001NVe": "53",
    "L10001NVE": "270",
    "L10000vxD": "157",
    "L10001NVp": "94",
    "L10000vXs": "157",
    "L10001NVx": "89",
    "L10001NVX": "265",
    "L10001NVz": "224",
    "L10001NW1": "224",
    "L10000vYG": "157",
    "L10000w55": "157",
    "L10001NWe": "15",
    "L10001NWH": "270",
    "L10001NWl": "53",
    "L10001NWn": "265",
    "L10001NWW": "265",
    "L10001NX6": "224",
    "L10001NX8": "53",
    "L10001NXa": "224",
    "L10001NXd": "191",
    "L10001NXD": "224",
    "L10001NXg": "224",
    "L10001NXH": "262",
    "L10001NXL": "46",
    "L10001NXM": "83",
    "L10000w5t": "157",
    "L10001NXO": "262",
    "L10001NXU": "53",
    "L10001NXV": "69",
    "L10001NXX": "42",
    "L10001NXy": "265",
    "L10001NY0": "265",
    "L10001NY1": "265",
    "L10001NY3": "265",
    "L10001NY4": "42",
    "L10001NY5": "15",
    "L10001NYc": "270",
    "L10001NYG": "265",
    "L10001NYh": "271",
    "L10001NYj": "110",
    "L10001NYk": "64",
    "L10000w9I": "157",
    "L10001NYO": "233",
    "L10001NYQ": "237",
    "L10000wAD": "157",
    "L10001NYU": "117",
    "L10001NZ8": "64",
    "L10001NZE": "224",
    "L10001NZh": "53",
    "L10001NZI": "262",
    "L10001NZJ": "53",
    "L10001NZk": "46",
    "L10001NZL": "265",
    "L10001NZn": "224",
    "L10001NZo": "265",
    "L10001NZp": "291",
    "L10000wey": "157",
    "L10001NZs": "174",
    "L10001NZS": "109",
    "L10001NZV": "42",
    "L10001NZW": "42",
    "L10000wgO": "157",
    "L10001NZZ": "265",
    "L10008cAL": "270",
    "L10008cAO": "270",
    "L10008G0q": "229",
    "L10008gRo": "127",
    "L10008gRv": "127",
    "L10001N5x": "157",
    "L10001N5Y": "157",
    "L10001N81": "157",
    "L10001N9t": "157",
    "L10001NAm": "157",
    "L10001NbA": "157",
    "L10001Nbm": "157",
    "L10001NBS": "157",
    "L10001Nbx": "157",
    "L10001Nc3": "157",
    "L10001NCJ": "157",
    "L10001NCW": "157",
    "L10001NCx": "157",
    "L10008noP": "151",
    "L10008OB0": "265",
    "L10008OBF": "265",
    "L10008pre": "42",
    "L10001NCY": "157",
    "L10001Ncz": "157",
    "L10001NdH": "157",
    "L10008UrO": "284",
    "L10001NDm": "157",
    "L10001NDP": "157",
    "L10001NE3": "157",
    "L10001NEd": "157",
    "L10001NeY": "157",
    "L10001Nf2": "157",
    "L10008yt4": "120",
    "L10008yt7": "69",
    "L10008ytA": "69",
    "L10008ytD": "233",
    "L10008ytH": "233",
    "L10008ytL": "233",
    "L10008ytP": "233",
    "L10008ytT": "233",
    "L1000903w": "265",
    "L1000904B": "265",
    "L10009126": "265",
    "L1000912C": "265",
    "L1000912O": "265",
    "L10001NF8": "157",
    "L10001NFA": "157",
    "L10001NfM": "157",
    "L10001NG0": "157",
    "L100093vb": "42",
    "L100093vD": "265",
    "L100093vL": "265",
    "L100093vr": "42",
    "L100093wA": "110",
    "L100093wm": "110",
    "L100093wM": "265",
    "L100093wn": "137",
    "L100093wx": "265",
    "L100093wX": "265",
    "L100093x3": "265",
    "L100093x9": "265",
    "L100093xE": "265",
    "L100093xg": "265",
    "L100093xJ": "265",
    "L100093xL": "265",
    "L100093xn": "265",
    "L100093xp": "265",
    "L100093xv": "265",
    "L100093xY": "265",
    "L100093xz": "265",
    "L100093y3": "265",
    "L100093y7": "265",
    "L10009408": "42",
    "L1000940B": "110",
    "L100094SC": "265",
    "L100094SI": "265",
    "L100094SM": "265",
    "L100094Vn": "206",
    "L100094VO": "206",
    "L100094VV": "206",
    "L100094VZ": "206",
    "L100095Re": "83",
    "L100095Rm": "83",
    "L100095RO": "83",
    "L100095RS": "83",
    "L100095Ru": "83",
    "L100095U1": "176",
    "L100095U2": "117",
    "L100095UH": "262",
    "L100095UP": "262",
    "L100095UT": "262",
    "L100095UX": "262",
    "L100098Ef": "0",
    "L100098EH": "0",
    "L100098EL": "0",
    "L100098En": "228",
    "L100098EP": "0",
    "L100098Eq": "173",
    "L100098Ev": "228",
    "L100098EX": "0",
    "L100098Ey": "173",
    "L100098F3": "0",
    "L100098Fc": "63",
    "L100098FE": "201",
    "L100098Fi": "63",
    "L100098FI": "201",
    "L100098FL": "201",
    "L100098Fn": "63",
    "L100098FQ": "63",
    "L100098Fv": "63",
    "L100098FW": "63",
    "L100098G1": "63",
    "L100098G7": "63",
    "L100098Gc": "201",
    "L100098Gh": "201",
    "L100098GL": "201",
    "L100098GR": "201",
    "L100098GW": "201",
    "L100098GZ": "158",
    "L100098HE": "156",
    "L100098Hf": "162",
    "L100098HG": "156",
    "L100098HJ": "0",
    "L100098Hn": "156",
    "L100098Hs": "156",
    "L100098Hx": "156",
    "L100098HX": "162",
    "L200000AI": "42",
    "L10001NGc": "157",
    "L270000M9": "11",
    "L2H0000gf": "221",
    "L2M0000na": "83",
    "L2M0000nX": "83",
    "L2M0000ny": "83",
    "L2M0000o0": "83",
    "L2M0000o2": "83",
    "L2M0000o5": "83",
    "L2M0000oU": "83",
    "L10001NGH": "157",
    "L10001NgM": "157",
    "L2Q0001In": "224",
    "L2Q0001Iv": "224",
    "L2Q0001J8": "224",
    "L2Q0001JE": "224",
    "L2Q0001JJ": "224",
    "L10001NHF": "157",
    "L10001NNV": "157",
    "L10001NPa": "157",
    "L10001NPT": "157",
    "L10001NPV": "157",
    "L10001NQX": "157",
    "L10001NRL": "157",
    "L3d0000D6": "64",
    "L3d0000D7": "64",
    "L3J00003L": "291",
    "L3J00003M": "291",
    "L3J00003N": "291",
    "L3J00003S": "291",
    "L3v0001Wy": "280",
    "L4X0000Mj": "64",
    "L4X0000Mr": "64",
    "L4X0000MZ": "64",
    "L4X0000N2": "64",
    "L4X0000NA": "64",
    "L4X0000NN": "64",
    "L4X0001Cy": "11",
    "L4X0001D3": "11",
    "L5K0000O9": "58",
    "L5K0000P4": "58",
    "L5W0000CJ": "53",
    "L5W0000D1": "5",
    "LF0000036": "110",
    "LF000003A": "110",
    "LF000003E": "110",
    "LF000003F": "110",
    "LF000004J": "265",
    "L10001NS2": "157",
    "L10001NTb": "157",
    "L10001NTI": "157",
    "L10001NVM": "157",
    "L10001NW8": "157",
    "L10001NWd": "157",
    "L10001NXN": "157",
    "L10001NYm": "157",
    "L10001NYR": "157",
    "L2r0001pe": "157",
    "L2r0001pL": "157",
    "L2r0001pt": "157",
    "L2r0001q6": "157",
    "L2r0001q7": "157",
    "L2r0001qe": "157",
    "L2r0001qM": "157",
    "LS00000Fo": "157",
    "LS00000G3": "157",
    "LS00000GC": "157",
    "LS00000Gc": "157",
    "LG00000eW": "94",
    "LO00000aA": "174",
    "LO00000lj": "262",
    "LO00000WH": "291",
    "LO00000Wj": "291",
    "LO00000Wo": "291",
    "LO00000WP": "291",
    "LO00000Wr": "291",
    "LO00000Wz": "291",
    "LO00000X0": "291",
    "LO00000X4": "291",
    "LO00000X8": "291",
    "LO00000Xb": "291",
    "LO00000Xc": "291",
    "LO00000XE": "291",
    "LO00000XM": "291",
    "LO00000Xr": "291",
    "LO00000XT": "291",
    "LO00000XU": "291",
    "LO00000Xz": "291",
    "LO00000Y4": "291",
    "LO00000Y8": "291",
    "LO00000Yc": "291",
    "LO00000YE": "291",
    "LO00000Yf": "121",
    "LO00000YM": "291",
    "LO00000YP": "121",
    "LO00000YU": "291",
    "LO00000YX": "121",
    "LO00000Yz": "121",
    "LO00000Z6": "57",
    "LO00000Zf": "15",
    "LO00000Zg": "141",
    "LO00000Zh": "78",
    "LO00000ZL": "15",
    "LO00000Zo": "272",
    "LO00000ZQ": "141",
    "LO00000Zv": "78",
    "LO00000ZX": "15",
    "LO00000ZY": "141",
    "LS000009i": "270",
    "LS000009m": "270",
    "LS000009q": "270",
    "LS000009t": "270",
    "LS000009y": "270",
    "LS00000A1": "270",
    "LS00000A6": "270",
    "LS00000A9": "270",
    "LS00000AE": "270",
    "LS00000AH": "270",
    "LS00000Au": "53",
    "LS00000AX": "270",
    "LS00000B2": "53",
    "LS00000BA": "53",
    "LS00000BD": "53",
    "LS00000BI": "53",
    "LS00000Bl": "53",
    "LS00000Bq": "46",
    "LS00000BQ": "53",
    "LS00000Bt": "53",
    "LS00000BX": "53",
    "LS00000BY": "53",
    "LS00000C1": "53",
    "LS00000C5": "46",
    "LS00000CA": "53",
    "LS00000CD": "46",
    "LS00000Ci": "216",
    "LS00000CL": "46",
    "LS00000Cp": "216",
    "LS00000Cq": "216",
    "LS00000CT": "46",
    "LS00000Cx": "216",
    "LS00000CY": "46",
    "LS00000D4": "216",
    "LS00000D7": "216",
    "LS00000Dc": "64",
    "LS00000DC": "216",
    "LS00000Dg": "64",
    "LS00000Do": "64",
    "LS00000DR": "64",
    "LS00000DY": "64",
    "LS00000Ec": "64",
    "LS00000En": "64",
    "LS00000Ev": "64",
    "LS00000EY": "64",
    "LS00000F0": "64",
    "LS00000FC": "64",
    "LS00000FL": "64",
    "LS00000FO": "64",
    "LS00000Gd": "157",
    "LS00000GF": "157",
    "LS00000FT": "64",
    "LS00000FW": "64",
    "LS00000Gk": "157",
    "LS00000FZ": "64",
    "LS00000GN": "157",
    "LS00000GR": "157",
    "LS00000Gs": "157",
    "LS00000GV": "157",
    "LS00000H5": "157",
    "LS00000HC": "157",
    "LS00000Hg": "157",
    "LS00000HH": "157",
    "LS00000HK": "157",
    "LS00000Ho": "157",
    "LS00000Hq": "157",
    "LS00000HT": "157",
    "LS00000HY": "157",
    "LS00000I1": "157",
    "LS00000IC": "157",
    "LS00000ID": "157",
    "Lz00001Ua": "157",
    "L10000s1d": "269",
    "L10000uwO": "286",
    "L10001Nd3": "286",
    "L10001NG3": "286",
    "LS00000Ib": "224",
    "L10000uGl": "290",
    "L10000uW0": "290",
    "LS00000If": "224",
    "LS00000IQ": "224",
    "LS00000Iu": "272",
    "LS00000IV": "224",
    "LS00000N9": "216",
    "LU00002UQ": "55",
    "LS00000Hb": "290",
    "Lz00001UL": "53",
    "Lz00001Um": "224",
    "Lz00001UT": "224",
}

# creating a list to reduce the number of rows
decentral_components_list = [
    "_north_pv",
    "_north_east_pv",
    "_east_pv",
    "_south_east_pv",
    "_south_pv",
    "_south_west_pv",
    "_west_pv",
    "_north_west_pv",
    "_north_solarthermal_source_collector",
    "_north_east_solarthermal_source_collector",
    "_east_solarthermal_source_collector",
    "_south_east_solarthermal_source_collector",
    "_south_solarthermal_source_collector",
    "_south_west_solarthermal_source_collector",
    "_west_solarthermal_source_collector",
    "_north_west_solarthermal_source_collector",
    "_gasheating_transformer",
    "_ashp_transformer",
    "_gchp_transformer",
    "_battery_storage",
    "_thermal_storage",
    "_electricheating_transformer",
    "_com_electricity_demand",
    "_res_electricity_demand",
    "_electricity_bus_shortage",
    "_pv_bus_excess",
    "_heat_bus",
    "pv_central",
    "",
]


def __remove_redundant_comps(components, decentral_components_from_csv, wo_pv=False):
    for comp in components["ID"]:
        i = comp.split("_")
        if "pv" not in i[0]:
            if "central" not in i[0]:
                if "RES" not in i[0] and "COM" not in i[0]:
                    if len(str(i[0])) <= 4:
                        decentral_components_from_csv.append(i[0])
    decentral_components_from_csv = set(decentral_components_from_csv)
    return decentral_components_from_csv


def __create_decentral_overview(components):
    # defining columns of the sheet including decentralized components
    decentral_columns = [
        "Cluster",
        "PV north",
        "Max. PV north",
        "PV north east",
        "Max. PV north east",
        "PV east",
        "Max. PV east",
        "PV south east",
        "Max. PV south east",
        "PV south",
        "Max. PV south",
        "PV south west",
        "Max. PV south west",
        "PV west",
        "Max. PV west",
        "PV north west",
        "Max. PV north west",
        "Installed PV",
        "Max. PV",
        "ST north",
        "Max. ST north",
        "ST north east",
        "Max. ST north east",
        "ST east",
        "Max. ST east",
        "ST south east",
        "Max. ST south east",
        "ST south",
        "Max. ST south",
        "ST south west",
        "Max. ST south west",
        "ST west",
        "Max. ST west",
        "ST north west",
        "Max. ST north west",
        "Installed ST",
        "Max. ST",
        "Gasheating-System",
        "ASHP",
        "GCHP",
        "Battery-Storage",
        "Thermal-Storage",
        "Electric Heating",
        "COM Electricity Demand",
        "RES Electricity Demand",
        "Electricity Import",
        "Electricity Export",
        "District Heating",
    ]
    # defining units for decentral components
    decentral_columns_units = {
        "Cluster": "",
        "PV north": "(kW)",
        "Max. PV north": "(kW)",
        "PV north east": "(kW)",
        "Max. PV north east": "(kW)",
        "PV east": "(kW)",
        "Max. PV east": "(kW)",
        "PV south east": "(kW)",
        "Max. PV south east": "(kW)",
        "PV south": "(kW)",
        "Max. PV south": "(kW)",
        "PV south west": "(kW)",
        "Max. PV south west": "(kW)",
        "PV west": "(kW)",
        "Max. PV west": "(kW)",
        "PV north west": "(kW)",
        "Max. PV north west": "(kW)",
        "Installed PV": "(kW)",
        "Max. PV": "(kW)",
        "ST north": "(kW)",
        "Max. ST north": "(kW)",
        "ST north east": "(kW)",
        "Max. ST north east": "(kW)",
        "ST east": "(kW)",
        "Max. ST east": "(kW)",
        "ST south east": "(kW)",
        "Max. ST south east": "(kW)",
        "ST south": "(kW)",
        "Max. ST south": "(kW)",
        "ST south west": "(kW)",
        "Max. ST south west": "(kW)",
        "ST west": "(kW)",
        "Max. ST west": "(kW)",
        "ST north west": "(kW)",
        "Max. ST north west": "(kW)",
        "Installed ST": "(kW)",
        "Max. ST": "(kW)",
        "Gasheating-System": "(kW)",
        "ASHP": "(kW)",
        "GCHP": "(kW)",
        "Battery-Storage": "(kWh)",
        "Thermal-Storage": "(kWh)",
        "Electric Heating": "(kW)",
        "COM Electricity Demand": "(kWh)",
        "RES Electricity Demand": "(kWh)",
        "Electricity Import": "(kWh)",
        "Electricity Export": "(kWh)",
        "District Heating": "(kW)",
    }

    decentral_components = pd.DataFrame(columns=decentral_columns)
    decentral_components = decentral_components.append(
        pd.Series(decentral_columns_units), ignore_index=True
    )

    decentral_components_from_csv = []

    decentral_components_from_csv = __remove_redundant_comps(
        components, decentral_components_from_csv
    )

    # import investment values from components.csv
    for i in decentral_components_from_csv:
        installed_power = []

        for comp in decentral_components_list:
            if comp not in [
                "_com_electricity_demand",
                "_res_electricity_demand",
                "_electricity_bus_shortage",
                "_pv_bus_excess",
                "_heat_bus",
            ]:
                # investment values of pv
                variable_central = (
                    components.loc[components["ID"].str.contains(str(i) + comp)][
                        "investment/kW"
                    ]
                ).values
                variable_central = (
                    float(variable_central[0]) if variable_central.size > 0 else 0
                )
            elif "_heat_bus" in comp:
                dh = 0
                for building in label_Cluster:
                    if label_Cluster[building] == i:
                        variable_building = (
                            components.loc[
                                components["ID"].str.contains(
                                    "-" + str(building) + comp
                                )
                            ]["investment/kW"]
                        ).values
                        variable_building = (
                            float(variable_building[0])
                            if variable_building.size > 0
                            else 0
                        )
                        dh += variable_building
            else:
                if comp != "_electricity_bus_shortage":
                    variable_central = (
                        components.loc[components["ID"].str.contains(str(i) + comp)][
                            "input 1/kWh"
                        ]
                    ).values
                    variable_central = (
                        float(variable_central[0]) if variable_central.size > 0 else 0
                    )
                else:
                    variable_central = (
                        components.loc[components["ID"].str.contains(str(i) + comp)][
                            "output 1/kWh"
                        ]
                    ).values
                    variable_central = (
                        float(variable_central[0]) if variable_central.size > 0 else 0
                    )
            installed_power.append(variable_central)
        maximums_pv = []
        maximums_st = []
        installed_pv = 0.0
        installed_st = 0.0
        celestial = [
            "north",
            "north_east",
            "east",
            "south_east",
            "south",
            "south_west",
            "west",
            "north_west",
        ]

        for test in celestial:
            # max values for each pv system,
            # need celestial to select the pv source
            maximum_pv = (
                components.loc[
                    components["ID"].str.contains(str(i) + "_" + test + "_pv_source")
                ]["max. invest./kW"]
            ).values
            maximum_st = (
                components.loc[
                    components["ID"].str.contains(
                        str(i) + "_" + test + "_solarthermal_source_collector"
                    )
                ]["max. invest./kW"]
            ).values

            if maximum_pv.size > 0:
                maximums_pv.append(float(maximum_pv[0]))
            else:
                maximums_pv.append(0)
            if maximum_st.size > 0:
                maximums_st.append(float(maximum_st[0]))
            else:
                maximums_st.append(0)

        # iterate through decentral components list
        for test2 in range(8):
            installed_pv_roof = (
                components.loc[
                    components["ID"].str.contains(
                        str(i) + decentral_components_list[test2]
                    )
                ]["investment/kW"]
            ).values
            installed_pv_roof = (
                float(installed_pv_roof[0]) if installed_pv_roof.size > 0 else 0
            )
            installed_pv = installed_pv + installed_pv_roof
            installed_st_roof = (
                components.loc[
                    components["ID"].str.contains(
                        str(i) + decentral_components_list[8 + test2]
                    )
                ]["investment/kW"]
            ).values
            installed_st_roof = (
                float(installed_st_roof[0]) if installed_st_roof.size > 0 else 0
            )
            installed_st = installed_st + installed_st_roof

        max_total_pv = sum(maximums_pv)
        max_total_st = sum(maximums_st)

        # dict to append the values
        decentral_components_dict = {
            "Cluster": str(i),
            "PV north": installed_power[0],
            "Max. PV north": maximums_pv[0],
            "PV north east": installed_power[1],
            "Max. PV north east": maximums_pv[1],
            "PV east": installed_power[2],
            "Max. PV east": maximums_pv[2],
            "PV south east": installed_power[3],
            "Max. PV south east": maximums_pv[3],
            "PV south": installed_power[4],
            "Max. PV south": maximums_pv[4],
            "PV south west": installed_power[5],
            "Max. PV south west": maximums_pv[5],
            "PV west": installed_power[6],
            "Max. PV west": maximums_pv[6],
            "PV north west": installed_power[7],
            "Max. PV north west": maximums_pv[7],
            "Installed PV": installed_pv,
            "Max. PV": max_total_pv,
            "ST north": installed_power[8],
            "Max. ST north": maximums_st[0],
            "ST north east": installed_power[9],
            "Max. ST north east": maximums_st[1],
            "ST east": installed_power[10],
            "Max. ST east": maximums_st[2],
            "ST south east": installed_power[11],
            "Max. ST south east": maximums_st[3],
            "ST south": installed_power[12],
            "Max. ST south": maximums_st[4],
            "ST south west": installed_power[13],
            "Max. ST south west": maximums_st[5],
            "ST west": installed_power[14],
            "Max. ST west": maximums_st[6],
            "ST north west": installed_power[15],
            "Max. ST north west": maximums_st[7],
            "Installed ST": installed_st,
            "Max. ST": max_total_st,
            "Gasheating-System": installed_power[16],
            "ASHP": installed_power[17],
            "GCHP": installed_power[18],
            "Battery-Storage": installed_power[19],
            "Thermal-Storage": installed_power[20],
            "Electric Heating": installed_power[21],
            "COM Electricity Demand": installed_power[22],
            "RES Electricity Demand": installed_power[23],
            "Electricity Import": installed_power[24],
            "Electricity Export": installed_power[25],
            "District Heating": dh,
        }

        decentral_components = decentral_components.append(
            pd.Series(decentral_components_dict), ignore_index=True
        )

    return decentral_components


def __create_decentral_overview_energy_amount(components):
    decentral_columns = [
        "Cluster",
        "PV north",
        "PV north east",
        "PV east",
        "PV south east",
        "PV south",
        "PV south west",
        "PV west",
        "PV north west",
        "Produced Amount PV",
        "PV excess",
        "PV->Central",
        "clusterintern consumption",
        "Total_Production - PV excess",
    ]
    # "ST north", "Max. ST north", "ST north east", "Max. ST north east",
    # "ST east", "Max. ST east", "ST south east", "Max. ST south east",
    # "ST south", "Max. ST south", "ST south west", "Max. ST south west",
    # "ST west", "Max. ST west", "ST north west", "Max. ST north west",
    # "Installed ST", "Max. ST",
    # "Gasheating-System", "ASHP", "GCHP", "Battery-Storage",
    # "Thermal-Storage", "Electric Heating", "COM Electricity Demand",
    # "RES Electricity Demand", "Electricity Import", "Electricity Export",
    # "District Heating"]
    # defining units for decentral components
    decentral_columns_units = {
        "Cluster": "",
        "PV north": "(kWh)",
        "PV north east": "(kWh)",
        "PV east": "(kWh)",
        "PV south east": "(kWh)",
        "PV south": "(kWh)",
        "PV south west": "(kWh)",
        "PV west": "(kWh)",
        "PV north west": "(kWh)",
        "Produced Amount PV": "(kWh)",
        "PV excess": "(kWh)",
        "PV->Central": "(kWh)",
        "clusterintern consumption": "(kWh)",
        "Total_Production - PV excess": "(kWh)",
    }

    decentral_components = pd.DataFrame(columns=decentral_columns)
    decentral_components = decentral_components.append(
        pd.Series(decentral_columns_units), ignore_index=True
    )

    decentral_components_from_csv = __remove_redundant_comps(components, [], wo_pv=True)

    for i in decentral_components_from_csv:
        installed_power = []
        installed_pv = 0.0
        for comp in decentral_components_list:
            if "pv" in comp:
                print(comp)
                if "excess" in comp or "central" in comp:
                    variable_central = (
                        components.loc[components["ID"].str.contains(str(i) + comp)][
                            "input 1/kWh"
                        ]
                    ).values
                else:
                    # investment values of pv
                    variable_central = (
                        components.loc[components["ID"].str.contains(str(i) + comp)][
                            "output 1/kWh"
                        ]
                    ).values
                variable_central = (
                    float(variable_central[0]) if variable_central.size > 0 else 0
                )
                installed_power.append(variable_central)
        for test2 in range(8):
            installed_pv_roof = (
                components.loc[
                    components["ID"].str.contains(
                        str(i) + decentral_components_list[test2]
                    )
                ]["output 1/kWh"]
            ).values
            installed_pv_roof = (
                float(installed_pv_roof[0]) if installed_pv_roof.size > 0 else 0
            )
            installed_pv = installed_pv + installed_pv_roof
        decentral_components_dict = {
            "Cluster": str(i),
            "PV north": installed_power[0],
            "PV north east": installed_power[1],
            "PV east": installed_power[2],
            "PV south east": installed_power[3],
            "PV south": installed_power[4],
            "PV south west": installed_power[5],
            "PV west": installed_power[6],
            "PV north west": installed_power[7],
            "Produced Amount PV": installed_pv,
            "PV excess": installed_power[8],
            "PV->Central": installed_power[9],
            "clusterintern consumption": (
                installed_pv - (installed_power[8] + installed_power[9])
            ),
            "Total_Production - PV excess": (installed_pv - installed_power[8]),
        }
        decentral_components = decentral_components.append(
            pd.Series(decentral_components_dict), ignore_index=True
        )

    return decentral_components


def __create_central_overview(components):
    """
    Fetches the central component investment from components.csv and
    creates the data frame which later becomes the Excel sheet
    "central".

    :param components: pandas Dataframe consisting of the
                       components.csv data
    :type components: pd.Dataframe
    :return: -**central values** (pd.Dataframe)
    """
    # defining columns of the sheet including centralized components
    central_columns = ["label", "investment"]
    central_values = pd.DataFrame(columns=central_columns)
    central_components = []
    for comp in components["ID"]:
        k = comp.split("_")
        if k[0] == "central":
            if k[-1] in ["transformer", "storage", "link"]:
                if len(k) == len(set(k)):
                    central_components.append(comp)
    for comp in central_components:
        # investment values of central components
        variable_central = (
            components.loc[components_csv_data["ID"].str.contains(comp)][
                "investment/kW"
            ]
        ).values
        variable_central = (
            float(variable_central[0]) if variable_central.size > 0 else 0
        )
        central_components_dict = {"label": comp, "investment": variable_central}
        central_values = central_values.append(
            pd.Series(central_components_dict), ignore_index=True
        )

    return central_values


def __create_building_overview(components):
    # defining columns
    building_columns = [
        "Building",
        "heat demand",
        "insulation window",
        "insulation wall",
        "insulation roof",
        "district heating",
    ]
    building_columns_units = {
        "Building": "",
        "heat demand": "kWh",
        "insulation window": "kW",
        "insulation wall": "kW",
        "insulation roof": "kW",
        "district heating": "kW",
    }

    # creating data frame
    building_components = pd.DataFrame(columns=building_columns)
    building_components = building_components.append(
        pd.Series(building_columns_units), ignore_index=True
    )

    # components which we will select
    building_components_list = [
        "_heat_demand",
        "_window",
        "_wall",
        "_roof",
        "_heat_bus",
    ]
    building_components_from_csv = []
    for comp in components["ID"]:
        i = comp.split("_")
        if len(str(i[0])) == 9:
            if "central" not in i[0] and "clustered" not in i[0]:
                building_components_from_csv.append(i[0])
    building_components_from_csv = set(building_components_from_csv)

    for i in building_components_from_csv:
        installed_power = []
        for comp in building_components_list:
            if comp == "_heat_demand":
                variable_building = (
                    components.loc[components["ID"].str.contains(str(i) + comp)][
                        "input 1/kWh"
                    ]
                ).values
            elif comp == "_heat_bus":
                variable_building = (
                    components.loc[components["ID"].str.contains("-" + str(i) + comp)][
                        "investment/kW"
                    ]
                ).values
            else:
                variable_building = (
                    components.loc[components["ID"].str.contains(str(i) + comp)][
                        "investment/kW"
                    ]
                ).values
            variable_building = (
                float(variable_building[0]) if variable_building.size > 0 else 0
            )

            installed_power.append(variable_building)
        building_components_dict = {
            "Building": str(i),
            "heat demand": installed_power[0],
            "insulation window": installed_power[1],
            "insulation wall": installed_power[2],
            "insulation roof": installed_power[3],
            "district heating": installed_power[4],
        }
        building_components = building_components.append(
            pd.Series(building_components_dict), ignore_index=True
        )

    return building_components


def __create_summary(components):
    summary_columns = [
        "Component",
        "Component_Costs",
        "Component_Emissions",
        "Total Energy Demand",
        "Total Energy Usage",
    ]
    summary_columns_units = {
        "Component": "",
        "Component_Costs": "€/a",
        "Component_Emissions": "g/a",
        "Total Energy Demand": "",
        "Total Energy Usage": "",
    }
    # creating data frame
    summary_components = pd.DataFrame(columns=summary_columns)
    summary_components = summary_components.append(
        pd.Series(summary_columns_units), ignore_index=True
    )
    total_costs = 0
    total_constr_costs = 0
    for num, comp in components.iterrows():
        costs = "---"
        constr_costs = "---"
        if comp["periodical costs/CU"] not in [0, "0.0", "0"] or comp[
            "variable costs/CU"
        ] not in [0, "0.0", "0"]:
            costs = 0
            if comp["periodical costs/CU"] not in [0, "0.0", "0"]:
                costs += float(comp["periodical costs/CU"])
            if comp["variable costs/CU"] not in [0, "0.0", "0"]:
                costs += float(comp["variable costs/CU"])
            total_costs += costs
        if comp["constraints/CU"] not in [0, "0.0", "0"]:
            constr_costs = float(comp["constraints/CU"])
            total_constr_costs += constr_costs
        if costs != "---" or constr_costs != "---":
            building_components_dict = {
                "Component": comp["ID"],
                "Component_Costs": str(costs),
                "Component_Emissions": str(constr_costs),
                "Total Energy Demand": "---",
                "Total Energy Usage": "---",
            }
            summary_components = summary_components.append(
                pd.Series(building_components_dict), ignore_index=True
            )
    summary_csv_data = pd.read_csv("summary.csv")
    row = next(summary_csv_data.iterrows())[1]
    building_components_dict = {
        "Component": "TOTAL",
        "Component_Costs": (str(round((total_costs / 1000000), 3)) + " Mio. €/a"),
        "Component_Emissions": (
            str(round((total_constr_costs / 1000000), 3)) + " t CO2/a"
        ),
        "Total Energy Demand": (
            str(round((row["Total Energy Demand"] / 1000000), 3)) + " GWh/a"
        ),
        "Total Energy Usage": (
            str(round((row["Total Energy Usage"] / 1000000), 3)) + " GWh/a"
        ),
    }
    summary_components = summary_components.append(
        pd.Series(building_components_dict), ignore_index=True
    )
    return summary_components


def urban_district_upscaling_post_processing_clustered(components: str):
    """
    todo docstring
    """
    components_csv = pd.read_csv(components)
    components_csv = components_csv.replace(to_replace="---", value=0)
    # pre_scenario in order to import the labels
    decentral_comps = __create_decentral_overview(components_csv)
    central_comps = __create_central_overview(components_csv)
    building_comps = __create_building_overview(components_csv)
    # output
    writer = pd.ExcelWriter(
        os.path.dirname(__file__) + "/overview.xlsx", engine="xlsxwriter"
    )
    decentral_comps.to_excel(writer, "decentral_components", index=False)
    central_comps.to_excel(writer, "central_components", index=False)
    building_comps.to_excel(writer, "building_components", index=False)
    print("Overview created.")
    writer.save()


if __name__ == "__main__":
    # csv which contains the exportable data
    components_csv_data = pd.read_csv("components.csv")

    # replace defect values with 0
    components_csv_data = components_csv_data.replace(to_replace="---", value=0)

    # pre_scenario in order to import the labels
    decentral_components = __create_decentral_overview(components_csv_data)
    central_values = __create_central_overview(components_csv_data)
    building_components = __create_building_overview(components_csv_data)
    decentral_components2 = __create_decentral_overview_energy_amount(
        components_csv_data
    )
    # summary = __create_summary(components_csv_data)
    # output
    writer = pd.ExcelWriter(
        os.path.dirname(__file__) + "/overview.xlsx", engine="xlsxwriter"
    )
    decentral_components.to_excel(writer, "decentral_components", index=False)
    decentral_components2.to_excel(writer, "decentral_components_amounts", index=False)
    central_values.to_excel(writer, "central_components", index=False)
    building_components.to_excel(writer, "building_components", index=False)
    # summary.to_excel(writer, "summary", index=False)
    writer.save()

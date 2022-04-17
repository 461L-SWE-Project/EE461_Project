import wfdb
import json
from flask import Blueprint


datasets = Blueprint('datasets', __name__)
datasetMatrix = [ #We should eventually move this into the mongoDB
    {"pName":"100","link":"https://physionet.org/files/mitdb/1.0.0/100.dat?download"}, #pName = the record name in the physionet database, link is link to download it
    {"pName":"101","link":"https://physionet.org/files/mitdb/1.0.0/101.dat?download"},
    {"pName":"102","link":"https://physionet.org/files/mitdb/1.0.0/102.dat?download"},
    {"pName":"103","link":"https://physionet.org/files/mitdb/1.0.0/103.dat?download"},
    {"pName":"104","link":"https://physionet.org/files/mitdb/1.0.0/104.dat?download"}
]
physioDir = "mitdb/1.0.0/"

@datasets.route('/get_datasets', methods=['GET'])
def getDatasets():
    returnArr = []
    for dataset in datasetMatrix:
        record = wfdb.rdrecord(record_name=dataset["pName"],pn_dir=physioDir)
        returnObj = {
            "record_name": record.record_name,
            "comments": record.comments,
            "n_sig": record.n_sig,
            "fs": record.fs,
            "sig_name": record.sig_name,
            "sig_len": record.sig_len,
            "link": dataset["link"]
        }
        returnArr.append(returnObj);
    return {
        "datasets": returnArr
    }
getDatasets()
from distutils.log import warn
import json
from locale import currency
import os
from tabnanny import filename_only
from webbrowser import get
from app import app
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename

from invoice2data import extract_data
from invoice2data.extract.loader import read_templates

ALLOWED_EXTENSIONS = set(['pdf'])

# converts currency data to a float value


def currency_data_to_foat(ammount):
    return float(ammount.replace(',', '').replace('$', ''))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/file-upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        templates = read_templates('Template/')  # load templates
        # writes pdf to dictionary result
        result = extract_data('testcase/' + filename, templates=templates)
        if (not result):
            resp = jsonify(
                {'message': 'This PDF is currently not supported please make sure that you are using a orignal statment.'})
            resp.status_code = 400
            return resp
        # delete the file
        if os.path.exists('testcase/' + filename):
            os.remove('testcase/' + filename)
        else:
            print("The file does not exist not removed")
        
        processingFee = 0
        transaction_fees = result["TRANSACTION_FEES"]
        for tfee in transaction_fees:
            name = tfee['TRANSACTION_FEES']
            type = tfee["Type"]
            if ("AUTH FEE" in name) and (type == "Fees"):
                processingFee += currency_data_to_foat(tfee['Amount'])
  
 
        total_account_fees = result["TOTAL_ACCOUNT_FEES"]
        for afee in total_account_fees:
            name = afee['ACCOUNT']
            type = afee["Type"]
            if ("AUTH FEE" in name) and (type == "Fees"):
                processingFee += currency_data_to_foat(afee['Amount'])

    
        result['Processing_Fee'] = str(round(processingFee, 2))
        result['Processing_Percent'] = str(round((processingFee/result['amount']*100), 2))
        result['Effective_Rate'] = str(
            round((currency_data_to_foat(result['Fees'][1])/result['amount']*100), 2))
        result['Average_Ticket'] = str(
            round(result['amount']/(len(result["SUMMARY_BY_DAY"])-2), 2))
        resp = json.dumps(result, indent=4, sort_keys=True, default=str)

        return resp
    else:
        resp = jsonify(
            {'message': 'PDF is the only alowed file type'})
        resp.status_code = 400
        return resp


if __name__ == "__main__":
    app.run()

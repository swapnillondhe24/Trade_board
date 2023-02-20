import re
import os
import json
from datetime import datetime
from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask import request,Response
from flask_cors import CORS
from helpers.tradeinfo import run_processes
from helpers.strategy_pnl import get_pnl_df_strategy, unrealised_profit_df_strategy, realized_profit_df_strategy



api = ''
app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_HEADERS'] = 'Content-Type'


class run_live_strategy(Resource):
    def generate(self,req):
        while True:
            trade_result = next(run_processes(req['symbol']))
            # trade_result="Hello this is being yielded"
            return f"data: {trade_result}\n\n"
            
    def post(self):
        try:
            request_json = request.get_json()
            return Response(self.generate(request_json), mimetype="text/event-stream")
            # return Response(request_json)
        except Exception as error:
            print(error)
            
from helpers.TradeInformation import get_all_positions
class getPositions(Resource):
    def getPositons(self):
        return get_all_positions()
    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.getPositons(), mimetype="text/event-stream")
            # return Response(request_json)
        except Exception as error:
            print(error)
            

class unrealisedprofitdfstrategy(Resource):
    def getUnrealizedPnl(self):
        return unrealised_profit_df_strategy()
    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.getUnrealizedPnl(), mimetype="text/event-stream")
            # return Response(request_json)
        except Exception as error:
            print(error)
            
class realizedProfitDfDtrategy(Resource):
    def getRealizedPnl(self):
        return realized_profit_df_strategy()
    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.getRealizedPnl(), mimetype="text/event-stream")
            # return Response(request_json)
        except Exception as error:
            print(error)
            
class getpnldfstrategy(Resource):
    def getPnlStrategy(self):
        return get_pnl_df_strategy(unrealised_profit_df_strategy(),realized_profit_df_strategy())
    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.getPnlStrategy())
            # return Response(request_json)
        except Exception as error:
            print(error)

            
# def run_live_strategy():
     
# if __name__ == "__main__":
#     app.run(debug=True)
        
# api.add_resource(run_live_strategy, '/runlivestrategy/')
api.add_resource(getPositions, '/getPositions/')
api.add_resource(getpnldfstrategy, '/getpnlstrategy/')
api.add_resource(realizedProfitDfDtrategy, '/getrealizedpnl/')
api.add_resource(unrealisedprofitdfstrategy, '/getunrealizedpnl/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
    app.run(debug=False)
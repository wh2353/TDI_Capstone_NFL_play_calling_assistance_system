from urllib import request
from flask import Flask, render_template, request
import bz2
import pickle
import dill
import _pickle as cPickle
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge


from model_class import linear_plus_nonlinear







def list_all_PassType_Rushdirection(formation_df, final_Pass_Rush_combined):
	'''
	Deifne function to generate all Pass and Rush play combinations
	'''
	return_df = pd.concat([formation_df.iloc[0,:]]*final_Pass_Rush_combined.shape[0], axis=1, ignore_index=True).T

	return_df.loc[:,final_Pass_Rush_combined.columns.tolist()] = final_Pass_Rush_combined


	return(return_df)



def sigmoid(alpha, x):
    '''
    Define sigmoid function to convert y pred value to probabilities (chance of success)
    '''
    return 1.0 / (1.0 + np.exp(0-alpha*x))



def python_to_football(res_row, final_res_df):
    
    '''
	For each row in the head, translate it into football language with success rate (as sigmoid y pred)
	'''
    formation = ""
    playType = ""
    passType = ""
    rushDirection = ""
    successRate = ""
    
    list_columns = final_res_df.columns.tolist()
    
    assert len(res_row) == len(list_columns)
    
    for i in range(len(res_row)):
        
        if "Formation_" in list_columns[i] and res_row[i] == 1:
            formation = list_columns[i].split("_")[1]
        
        if "PlayType_PASS" in list_columns[i] and res_row[i] == 1:
            playType = "PASS"
        elif "PlayType_RUSH" in list_columns[i] and res_row[i] == 1:
            playType = "RUSH"
        
        if "PassType_" in list_columns[i] and res_row[i] == 1:
            passType = list_columns[i].split("_")[1]
            
        if "RushDirection_" in list_columns[i] and res_row[i] == 1:
            rushDirection = list_columns[i].split("_")[1]
        
        if "sigmoid_" in list_columns[i]:
            successRate = f"{round(res_row[i]*100, 2)}%"
                   
    
    if passType != "":
        return(f"{formation} Formation, {playType} Play, {passType}, with {successRate} chance of Success.")
    elif rushDirection != "":
        return(f"{formation} Formation, {playType} Play, {rushDirection}, with {successRate} chance of Success.")






# Declare Flask
app = Flask(__name__)

@app.route("/")
def home():
	return render_template("home_page.html")


@app.route("/result")
def result():
	
	
	#step 1: get form data
	form_data = request.args

	year = int(form_data.get('Year'))
	offenseTeam = form_data.get('OffenseTeam')
	defenseTeam = form_data.get('DefenseTeam')

	Quarter = int(form_data.get('Quarter'))
	minutes = int(form_data.get('Minute'))
	seconds = int(form_data.get('Second'))

	Down = int(form_data.get('Down'))

	Yardline = int(form_data.get('Yardline'))

	togo = int(form_data.get('Yards needed'))

	#step 2: load the trained model
	
	#pickle does not work on Heroku with model with self-defined classes
	#Don Fox (TDI instructor) suggested to using dill instead (need to set recurse=True during dill.dump) 	
	with open ("model_data/050122_linear_non_linear_model_trained_dill.pkl", "rb") as f:
		mixed_best = dill.load(f)

	print("Finished loading the trained model!")


	#step 3: load the full combined data
	with bz2.BZ2File("model_data/20220428_final_combined_NFL_data.pbz2", "rb") as f:
		final_combined_data = cPickle.load(f)
    
	print(f"The preprocessed data shape is {final_combined_data.shape}")


	#step 4: make predictions and output Top 5 results in "football" language


	#step 4.0: get the subset for the designated offenseTeam, defenseTeam and seanson year
	


	#Important note: Not all teams have game against each other in a season
	#step 1 get all the data for a given offense team in a season
	offense_data = final_combined_data.loc[np.logical_and(final_combined_data.OffenseTeam==offenseTeam, \
	                                                         final_combined_data.SeasonYear==year)].reset_index(drop=True)
	#step 2 get all the data for a given offense team in a season
	defense_data = final_combined_data.loc[np.logical_and(final_combined_data.DefenseTeam==defenseTeam, \
	                                                         final_combined_data.SeasonYear==year)].reset_index(drop=True)
	#step 3 replace all the defence variables in the offensedata with the columns in the DefenseTeam
	offense_data.loc[:, [cname for cname in offense_data.columns if "Defense" in cname]] = \
	pd.concat([defense_data.loc[0, [cname for cname in offense_data.columns if "Defense" in cname]]]\
	          *offense_data.shape[0], axis=1, ignore_index=True).T

	subset_combined = offense_data


	del(defense_data)
	del(offense_data)


	
	#step 4.1: append all possible pass and rush plays to each available formation
	subset_combined = subset_combined.reset_index(drop=True)





	list_of_unique_PassType = [x.split("_")[1] for x in subset_combined.columns if "PassType" in x]

	list_of_unique_RushDirection = [x.split("_")[1] for x in subset_combined.columns if "RushDirection" in x]



	PassType_dummies = pd.get_dummies(list_of_unique_PassType, prefix='PassType')

	RushDirection_dummies = pd.get_dummies(list_of_unique_RushDirection , prefix='RushDirection')

	empty_RushDirection = pd.DataFrame(np.zeros(shape=(PassType_dummies.shape[0], len(list_of_unique_RushDirection))),
									columns=RushDirection_dummies.columns)
	empty_PassType = pd.DataFrame(np.zeros(shape=(RushDirection_dummies.shape[0], len(list_of_unique_PassType))),
									columns=PassType_dummies.columns)



	final_PassType_df = pd.concat([PassType_dummies, empty_RushDirection], axis=1)

	final_PassType_df['PlayType_PASS'] = 1
	final_PassType_df['PlayType_RUSH'] = 0


	final_RushDirection_df = pd.concat([empty_PassType, RushDirection_dummies], axis=1)

	final_RushDirection_df ['PlayType_PASS'] = 0
	final_RushDirection_df ['PlayType_RUSH'] = 1


	final_Pass_Rush_combined = pd.concat([final_PassType_df, final_RushDirection_df], axis=0, ignore_index=True)




	subset_combined = subset_combined.groupby(['Formation']).apply(lambda x: list_all_PassType_Rushdirection(x, final_Pass_Rush_combined))


	#update user defined values

	subset_combined["Time_in_seconds"] = Quarter*15*60 - minutes*60 - seconds 

	subset_combined["YardLine"] = Yardline


	subset_combined["Down"] = Down

	#prepare the test dataset
	all_combination_test = subset_combined.drop(columns=["SeriesFirstDown", "GameId", "GameDate", 
                                     "ToGo", "Yards", "Description", "SeasonYear",
                                      "Formation", "OffenseTeam", "DefenseTeam", "Quarter", "Minute", "Second", "Yards_vs_ToGo"
                                     ], axis=1)


	#make predictions, calcualte chance of success and output Top 5 in football language
	y_pred = mixed_best.predict(all_combination_test)


	sigmoid_y_pred = [sigmoid((max(100-Yardline-togo, 0)+50)/100, x - Down/2) for x in y_pred]


	all_combination_test["sigmoid_y_pred"] = sigmoid_y_pred


	final_res_df = all_combination_test.sort_values(["sigmoid_y_pred"], ascending=False).head()


	final_dict = final_res_df.apply(lambda x: python_to_football(x, final_res_df), axis=1).reset_index(drop=True).to_dict()

	"""return_str = ''

	for key, value in final_dict.items():
		return_str += f"Choice {key+1}: {value}<br>"


	print(f"result is {return_str}")"""
	return render_template("result.html", data=final_dict)

if __name__ == '__main__':
    app.run()
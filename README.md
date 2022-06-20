# NFL Play Calling Assistance System<br>
<b>The Data Incubator (TDI) Capstone Project</b><br>
<b>Author:</b> Wenrui Huang<br>
<b>Date: </b> 2022-06-09<br>
<b>Heroku Web App: </b> [Click Here](https://nfl-play-calling-assistant.herokuapp.com/) 
## Summary
In this project, I built a web app (based on a machine learning model) that can assist NFL coaches make play calls during a game in order to boost a team’s chance of winning, ultimately attracting more fans and bringing in more revenue for the organization.  
## Project Statement
The national football league (NFL), the world’s most profitable sports league, is highly competitive and each game determines a team’s fate. During the game, NFL coaches need to make play calls within 40 seconds, often facing a tremendous amount of pressure, thus tend to be error-prone. Based on the above, I propose a machine learning model (deployed as a web app) in which the coaches first submit the game information and then be provided with a list of suggested plays ranked based on chance of success to assist them make the right call during the game.
## Project Description
The goal of this project is to build a web application that can take game information from the user, process by a machine learning model and return a list of recommended plays ranked by chance of success for the user to choose from. 

### Step 1. Dataset Construction
In order to achieve this, two sets of data were utilized to build the model. The first set is the NFL play by play dataset , which includes every play of all 32 NFL teams from season year 2018 to 2021. The other dataset is the Madden NFL player rating data, which contains ratings in 43 categories of each player of all 32 NFL teams from season year 2018 to 2021.
The play by play dataset can be downloaded directly through [NFLsavant](http://nflsavant.com/about.php), in which the data for each season year were listed in separate csv tables thus need to be further combined to generate the full dataset. Exploratory data analysis was then performed with pandas profiling on the full dataset, to investigate missing values and potential correlations among variables. Finally, the full dataset were filtered and categorical features were converted to one-hot vectors for further processing.

The Madden NFL player ratings data can be accessed through [Madden Ratings](https://maddenratings.weebly.com), and downloaded using web scraping. The 2021 season data for all 32 teams were summarized in one excel table while the 2018-2020 season data were listed separately for each NFL team, thus needing to be further combined. After obtaining all the data, the rating category columns need to be renamed to make sure that the same kind of rating has the same name across all four datasets. Finally, one-hot encoded vectors were applied to replace categorical features.

During an NFL game, different formations may be used for different plays, and the players for a team on the court may vary according to play and formations, and a team may exchange or add/retire players during the off-season. Thus, in order to create a NFL play by play and player rating combined dataset for all seasons, players were selected based on their positions according to different formations listed in this wiki page and those with higher ratings were selected first. This process will be repeated for every team for each of four season years to form the final combined dataset.

### Step 2. Exploratory Analysis before Modeling
Before modeling, a simple exploratory data analysis was performed on combined dataset to see whether those NFL teams can be separated based on their offense or defense features. In order to achieve this, I extracted either offense or defense features only, and performed PCA on both subsets. As shown in the figures below, MIA and BAL stand out as outliers for offense while CAR, PHI and ARI seem to be defense outliers. This result is as expected, as in recently years, MIA is notorious for lacking of run offense while the QB of BAL, Lamar Jackson, is one of the leading rushers in the league; on the other hand, PHI and CAR have weakness in pass protection while ARI has lots of issues in run defense.<br>
OffenseTeam PCA Plot       |  DefenseTeam PCA Plot
:-------------------------:|:-------------------------:
 <img src="readme_images/NFL_offense.png" width=425 height=330>  |   <img src="readme_images/NFL_defense.png" width=425 height=330>  <br>

In order to further verify what we have observed from the PCA plots, random forest regression model were applied to delineate the important of each features in those offense or defense outliers in response to yard gain/loss during a play. As demonstrated in the bar plots below, BAL's offense is dominanted by rush plays while MIA mainly relied on its pass plays; on the other hand, ARI have issues in defending 1st, 2nd plays as well as left end rushes while CAR defense is vulernable to deep left passes. Such findings agree well with observations in PCA plots, strongly suggesting the feasibilty of building a play calls prediction model based on these data.<br>

BAL Offense Breakdown     | | MIA Offense Breakdown
:-------------------------:|:-------------------------:|:-------------------------:
<img src="readme_images/BAL_offense_key_features.png" width=475 height=300> | | <img src="readme_images/MIA_offense_key_features.png" width=475 height=300>

ARI Defense Breakdown       | | CAR Defense Breakdown
:-------------------------:|:-------------------------: |:-------------------------:
<img src="readme_images/ARI_defense_key_features.png" width=475 height=300> | | <img src="readme_images/CAR_defense_key_features.png" width=475 height=300>
 
### Step 3. Model Creation
The model building started with creating a new response variable that measures the success of a play, defined as the function of yards needed against total yards gained during a play. Then the combined data, together with the response variable were splitted 80-20 into train and test datasets. Data were train, cross-validated and tested on a linear and non-linear mixed model, in which data were first fit with regularized linear regression model, such as ridge, then the residuals were further fitted into a non-linear random forest regression model and both results were combined to generate the final predictions from the model. The final model, together with a filtered combined dataset, where only records with unique offense/defense team, SeasonYear and Formation features were kept to reduce the memory usage, were pickled for being utilized by the web application. 

### Step 4. Web Application Deployment
The final product has been deployed as a web application on Heroku in which the user can input self-defined game information such as offense/defense team, time, down, yards, etc. This information will be paired with the players’ rating data matched to every possible formation and pass/rush direction combinations and further processed in the backend by the built machine learning model to create a list of predictions for all possible plays. Finally, the predictions were converted into probabilities as “chance of success” using self-defined sigmoid functions, and the top 5 plays with highest “chance of success” will be translated into “Football” language and output to the user for their references. 

The complete workflow of this project was described in the flowchart below:<br><br>

<img src="readme_images/nfl_flowchart.png" width=600 height=500><br>


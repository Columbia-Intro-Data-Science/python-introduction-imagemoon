import numpy as np
import pandas as pd
from scipy import io
from flask import Flask, render_template, json, request

grouped = pd.read_csv('../user_detail.csv',index_col=None)
grouped = grouped.drop(grouped.columns[0], axis=1)
df_user = pd.read_csv('../yelp_data/user1.csv', usecols=[15, 16, 18, 19, 21, 22])
GM = io.mmread('../diffsion operator')
df_business = pd.read_csv('../business_detail.csv')
df_business = df_business.drop(df_business.columns[0], axis=1)

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index2.html')


@app.route('/show_input_name')
def show_input_name():
    return render_template('input_name.html')


@app.route('/user_detail', methods=['POST'])
def third():
    num = request.form['inputnumber']
    number = int(num[0][0])
    detail = grouped.iloc[[number]]
    user_id = grouped.iloc[number].user_id
    self_name = df_user[df_user.user_id == user_id].name.values[0]
    user_city = grouped[grouped.user_id == user_id].city.values[0]
    grouped_city_ = grouped[grouped.city == user_city]
    N = len(grouped_city_)
    rest_city = df_business[df_business.business_city == user_city]
    print '1', type(rest_city), rest_city.shape
    M = len(rest_city)
    
#   Restaurant Recomendation
#   user eating habit
    habit_index = detail.drop(['user_id', 'city'], axis=1).values[0].argsort()[-3:][::-1]

    habit = grouped.columns.values[habit_index][:]

#   Search restaurant
    co_rest = np.empty(M)
    habit_ = grouped.iloc[[number]].values[0][1:-1].astype(np.float64)

    for i in xrange(M):
        bu_city_cat = rest_city.drop(['address', 'business_id', 'business_city', 'business_name'],axis=1).values[i].astype(np.float64)
        co_rest[i] = np.corrcoef(habit_,bu_city_cat)[0,1].astype(np.float64)
    co_rest[np.isnan(co_rest)] = 0.
    rec_rest_number = np.array(co_rest).argsort()[-3:][::-1]
    rec_rest_name = df_business.iloc[rec_rest_number].business_name.values

    # Meal Pal Recommendation
    co = np.empty(N)
    ub = grouped_city_.iloc[[number]].values[0][1:-1].astype(np.float64)
    for i in xrange(N):
        ua = grouped_city_.iloc[[i]].values[0][1:-1].astype(np.float64)
        co[i] = np.corrcoef(ua,ub)[0,1].astype(np.float64)

    co[np.isnan(co)] = 0.

    rec_user_number = np.array(co).argsort()[-4:-1][::-1]
    rec_user_id = grouped_city_.iloc[rec_user_number].user_id.values
    rec_user_name = []
    rec_user_fans = []
    rec_user_useful = []
    rec_user_rcount = []
    for i in xrange(3):
        rec_user_name.append(df_user[df_user.user_id == rec_user_id[i]].name.values[0])
        rec_user_fans.append(df_user[df_user.user_id == rec_user_id[i]].fans.values[0])
        rec_user_useful.append(df_user[df_user.user_id == rec_user_id[i]].useful.values[0])
        rec_user_rcount.append(df_user[df_user.user_id == rec_user_id[i]].review_count.values[0])
    return render_template('user_detail.html',
                           habit = habit,
                           self_name=self_name,
                           number=rec_user_number,
                           id=rec_user_id,
                           name=rec_user_name,
                           city=user_city,
                           business_name=rec_rest_name,
                           fans=rec_user_fans,
                           useful=rec_user_useful,
                           rcount=rec_user_rcount
                           )




if __name__ == "__main__":
    app.run(debug = True)

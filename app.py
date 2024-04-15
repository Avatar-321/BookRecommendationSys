
# from flask import Flask, render_template, request
# import pickle
# import numpy as np
# from sklearn.neighbors import NearestNeighbors

# popular_df = pickle.load(open('popular.pkl', 'rb'))
# pt = pickle.load(open('pt.pkl', 'rb'))
# books = pickle.load(open('books.pkl', 'rb'))
# similarity_scores = pickle.load(open('knn_model.pkl', 'rb'))

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html',
#                            book_name=list(popular_df['Book-Title'].values),
#                            author=list(popular_df['Book-Author'].values),
#                            image=list(popular_df['Image-URL-M'].values),
#                            votes=list(popular_df['num_ratings'].values),
#                            rating=list(popular_df['avg_rating'].values)
#                            )

# @app.route('/recommend')
# def recommend_ui():
#     return render_template('recommend.html')

# @app.route('/recommend_books', methods=['POST'])
# def recommend():
#     user_input = request.form.get('user_input')
    
#     # Check if user_input exists in pt.index
#     indices = np.where(pt.index == user_input)[0]
    
#     if len(indices) == 0:
#         # Handle case where user_input doesn't exist in pt.index
#         return "User input not found in dataset"
    
#     index = indices[0]
    
#     # Use kneighbors to find the nearest neighbors
#     distances, similar_items_indices = similarity_scores.kneighbors([pt.iloc[index]])
    
#     similar_items = similar_items_indices[0][1:5]  # Exclude the item itself and take top 4 similar items

#     data = []
#     for i in similar_items:
#         item = []
#         temp_df = books[books['Book-Title'] == pt.index[i]]
#         item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
#         item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
#         item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

#         data.append(item)

#     return render_template('recommend.html', data=data)

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, render_template, request, session, redirect, url_for
import pickle
import numpy as np
from sklearn.neighbors import NearestNeighbors

# Load your data and models
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('knn_model.pkl', 'rb'))

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Dummy user data for demonstration purposes
users = {'user1': 'password1', 'user2': 'password2'}

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    if 'username' in session:
        return render_template('recommend.html')
    else:
        return redirect(url_for('login'))

@app.route('/recommend_books', methods=['POST'])
def recommend():
    # Recommendation logic
    if 'username' in session:
        user_input = request.form.get('user_input')
        indices = np.where(pt.index == user_input)[0]

        if len(indices) == 0:
            return "User input not found in dataset"

        index = indices[0]

        distances, similar_items_indices = similarity_scores.kneighbors([pt.iloc[index]])
        similar_items = similar_items_indices[0][1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            data.append(item)

        return render_template('recommend.html', data=data)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            return render_template('signup.html', error='Username already exists')
        else:
            users[username] = password
            session['username'] = username
            return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

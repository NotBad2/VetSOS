from flask import Flask, render_template, request, jsonify, redirect, session
import openai
from pymongo import MongoClient
from bson import ObjectId
import googlemaps
import io
import base64
import os
from PIL import Image, ImageChops
import requests


app = Flask(__name__)

app.secret_key = 'your secret key'
OPENAI_API_KEY = "your openai key"
openai.api_key = OPENAI_API_KEY

def create_connection():
    client = MongoClient('localhost', 27017)  # Connect to the MongoDB server
    db = client['mydatabase']  # Create a new database
    collection = db['animal']



@app.route('/')
def index():
    create_connection()
    return render_template('index.html')

@app.route('/index')
def index2():
    return render_template('index.html')

@app.route('/animal1')
def animal1():
    # Connect to the database
    client = MongoClient('localhost', 27017)
    db = client['mydatabase']
    collection = db['mycollection']

    # Assuming the user is stored in the session
    user = session.get('user')

    if user is None:
        # Handle the case where the user doesn't exist
        return "User not found", 404

    # Get the user's animals
    user_in_db = collection.find_one({"_id": ObjectId(user['_id'])})

    if not user_in_db or 'animals' not in user_in_db or len(user_in_db['animals']) == 0:
        # Handle the case where the user doesn't have any animals
        return "No animals found", 404

    # Get the first animal
    animal = user_in_db['animals'][0]

    return render_template('animal1.html', animal=animal)

@app.route('/update-animal1', methods=['POST'])
def update_animal1():
    try:
        # Get the new data from the form
        animal_id = request.form.get('id')
        nome1 = request.form.get('nome1')
        especie1 = request.form.get('especie1')
        raca1 = request.form.get('raca1')
        data1 = request.form.get('data1')
        pelo1 = request.form.get('pelo1')
        cauda1 = request.form.get('cauda1')

        # Connect to the database
        client = MongoClient('localhost', 27017)
        db = client['mydatabase']
        collection = db['mycollection']

        # Assuming the user is stored in the session
        user = session.get('user')

        # Update the animal's data
        result = collection.update_one(
            {"_id": ObjectId(user['_id']), "animals.id": animal_id},
            {
                "$set": {
                    "animals.$.nome1": nome1,
                    "animals.$.especie1": especie1,
                    "animals.$.raca1": raca1,
                    "animals.$.data1": data1,
                    "animals.$.pelo1": pelo1,
                    "animals.$.cauda1": cauda1
                }
            }
        )

        # Check if the update was successful
        if result.modified_count == 0:
            return "No animal was updated", 400

        # Redirect the user to the same page
        return redirect('/animal1')
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500

@app.route('/registos')
def registos():
    return render_template('registos.html')

    

@app.route('/assistente-ai')
def assistente():
    return render_template('assistente-ai.html')

@app.route('/recomendados', methods=['GET', 'POST'])
def recomendados():
    if request.method == 'POST':
        # This is a POST request, so handle the location
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        # Use Google Maps to find nearby veterinarians
        gmaps = googlemaps.Client(key='maps api key')
        places_result = gmaps.places_nearby(location=f"{latitude},{longitude}", radius=5000, type='veterinary_care')

        # Filter places with rating >= 4.5
        places = [{'name': place['name'], 'rating': place.get('rating', 0), 'place_id': place['place_id']} for place in places_result['results']]
        places = [place for place in places if place['rating'] >= 4.5]
        # Return the list of top 7 places as a JSON response
        return jsonify(places[:7])

        # Return the list of top 7 places as a JSON response
        return jsonify(places[:7])

    return render_template('recomendados.html')

@app.route('/infanimais')
def infanimais():
    return render_template('infanimais.html')

@app.route('/profissionais')
def profissionais():
    return render_template('profissionais.html')

@app.route('/animaisperdidos')
def animaisperdidos():
    return render_template('animais-perdidos.html')

@app.route('/novoboletim')
def novoboletim():
    return render_template('novoboletim.html')

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    user = session.get('user')
    if request.method == 'POST':
        # This is a POST request, so handle the location
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        return "Location received", 200

    if user is None:
        # Handle the case where the user doesn't exist
        return "User not found", 404

    return render_template('perfil.html', user=user)

@app.route('/pgina-animais', methods=['GET', 'POST'])
def pgina():
    if request.method == 'POST':
        try:
            nome1 = request.form.get('nome1')
            especie1 = request.form.get('especie1')
            raca1 = request.form.get('raca1')
            data1 = request.form.get('data1')
            pelo1 = request.form.get('pelo1')
            cauda1 = request.form.get('cauda1')

            client = MongoClient('localhost', 27017)
            db = client['mydatabase']
            collection = db['mycollection']

            # Assuming the user is stored in the session
            user = session.get('user')

            # Create the animal
            animal = {
                "nome1": nome1,
                "especie1": especie1,
                "raca1": raca1,
                "data1": data1,
                "pelo1": pelo1,
                "cauda1": cauda1
            }

            # Add the animal to the user's animals array
            result = collection.update_one(
                {"_id": ObjectId(user['_id'])},
                {"$push": {"animals": animal}}
            )

            return redirect('/pgina-animais')
        except Exception as e:
            print(f"Error: {e}")
            return str(e), 500
    else:
        client = MongoClient('localhost', 27017)
        db = client['mydatabase']
        collection = db['mycollection']
        animals = collection.find()

        return render_template('pgina-animais.html', animals=animals)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            client = MongoClient('localhost', 27017)
            db = client['mydatabase']
            collection = db['mycollection']
            result = collection.insert_one({
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": password,
                "confirm_password": confirm_password,
                "telemovel": "",
                "data_de_nascimento": "",
                "genero": ""
            })


            return redirect('/perfil')
        except Exception as e:
            print(f"Error: {e}")
            return str(e), 500
    else:
        return render_template('register.html')

@app.route('/iniciar', methods=['GET', 'POST'])
def iniciar():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        client = MongoClient('localhost', 27017)
        db = client['mydatabase']
        collection = db['mycollection']
        user = collection.find_one({"email": email})

        if user and user['password'] == password:
            # Convert ObjectId to string before storing in session
            user['_id'] = str(user['_id'])
            session['user'] = user

            return redirect('/perfil')
        else:
            error = "Email ou palavra passe errada"

    return render_template('iniciar.html', error=error)

@app.route('/update-profile', methods=['POST'])
def update_profile():
    try:
        # Get the new data from the form
        user_id = session.get('user_id')  # Get user_id from the session
        print(f"User ID: {user_id}")
        first_name = request.form.get('first_name')
        telemovel = request.form.get('telemovel')
        email = request.form.get('email')
        password = request.form.get('password')
        data_de_nascimento = request.form.get('data')
        genero = request.form.get('genero')

        # Connect to the database
        client = MongoClient('localhost', 27017)
        db = client['mydatabase']
        collection = db['mycollection']

        # Update the user's profile
        result = collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "first_name": first_name,
                    "telemovel": telemovel,
                    "email": email,
                    "password": password,
                    "data_de_nascimento": data_de_nascimento,
                    "genero": genero
                }
            }
        )

        # Check if the update was successful
        if result.modified_count == 0:
            return "No user was updated", 400

        # Update the user data in the session
        user = collection.find_one({"_id": ObjectId(user_id)})
        session['user'] = user  # This line is causing the error

        # Convert ObjectId to string before storing in session
        user['_id'] = str(user['_id'])
        session['user'] = user

        # Redirect the user to their profile page
        return redirect('/perfil')
        
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500
        
@app.route('/process', methods=['POST'])
def process():
    user_input = request.form['prompt']

    if not any(word in user_input for word in ["cão", "cao", "cães", "caos", "cãos", "gato", "gatos", "pássaro", "passaro", "pássaros", "passaros", "peixe", "peixes", "cavalo", "cavalos", "vaca", "vacas", "porco", "porcos", "ovelha", "ovelhas", "galinha", "galinhas", "rato", "ratos"]):
        return jsonify({'message': 'Peço desculpa, mas só posso oferecer ajuda com questões relacionadas a animais.'})
    messages = [{"role": "user", "content": user_input}]

    # Initial prompt for the GPT model
    initial_prompt = {"role": "assistant", "content": "Eu sou um assistente AI. Estou aqui para ajudar tirar dúvidas relacionadas a animais.Não posso escrever texto corrido.Tenho apresentar todas as ideias em pontos, e não pode exceder 60 caaracters."}

    messages = [initial_prompt, {"role": "user", "content": user_input}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    chat_reply = response['choices'][0]['message']['content']

    # Update chat history with the new message
    messages.append({"role": "assistant", "content": chat_reply})

    return jsonify({'message': chat_reply})


def encode_image(image):
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def analyze_image_with_openai(uploaded_image, reference_image):
    base64_uploaded_image = encode_image(uploaded_image)
    base64_reference_image = encode_image(reference_image)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4o", 
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You will receive an image from an animal, your job is to compare the similarity between the two images, you should base yourself on the type of the animal, the color, the relative size, for example, if you receive an animal and the color is completely different it should be between 0-20, if their race is different it should be a lower score as well, if it's not even the same type of animal it should be 0. You should base yourself in whatever you find a good comparison term, I only gave a few examples, do as many comparisons as you can. Your response should only be a number between 0 and 100, nothing more, where 0 means the images are completely different and 100 means the images are identical. Remember compare the animals, not the images and only use the images as a reference. Only return a number between 0 and 100."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_uploaded_image}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_reference_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()
    
    # Extract the content from the response
    analysis_content = response_data['choices'][0]['message']['content']

    return analysis_content

def compare_with_reference_images(uploaded_image):
    # List of reference images in a specific folder
    reference_folder = 'static\public\imagens'
    reference_images = []

    for filename in os.listdir(reference_folder):
        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
            reference_image_path = os.path.join(reference_folder, filename)
            reference_image = Image.open(reference_image_path)

            # Analyze similarity with OpenAI
            similarity_score = analyze_image_with_openai(uploaded_image, reference_image)
            print(f"Similarity score with {filename}: {similarity_score}")
            reference_images.append({'image_path': reference_image_path, 'similarity_score': similarity_score})

    # Sort reference images based on similarity score
    reference_images = sorted(reference_images, key=lambda x: x['similarity_score'], reverse=True)

    return reference_images


@app.route('/compare', methods=['POST'])
def compare():
    try:
        uploaded_file = request.files['image'].read()
        uploaded_image = Image.open(io.BytesIO(uploaded_file))

        # Compare uploaded image with reference images
        reference_images = compare_with_reference_images(uploaded_image)

        return jsonify(reference_images)

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/comparison')
def comparison():
    return render_template('compare.html')

if __name__ == '__main__':
    app.run(debug=True) 
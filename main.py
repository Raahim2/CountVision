from flask import Flask ,render_template , request , redirect
import os
import json
import cv2
# from deepface import DeepFace

def mark_faces(photo_path):
    image = cv2.imread(photo_path)
    
    faces= DeepFace.extract_faces(img_path = image)

    for i in range(len(faces)):
        x, y, w, h = faces[i]["facial_area"]["x"], faces[i]["facial_area"]["y"], faces[i]["facial_area"]["w"], faces[i]["facial_area"]["h"]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  

    return image

def compair_faces(db_directory , photo):
    results ={}
    faces= DeepFace.extract_faces(photo)
    image = cv2.imread(photo)

    
    for i in range(len(faces)):
        x, y, w, h = faces[i]["facial_area"]["x"], faces[i]["facial_area"]["y"], faces[i]["facial_area"]["w"], faces[i]["facial_area"]["h"]
        face_img = image[y:y+h, x:x+w]
        cv2.imwrite(f"Temp/{i}.jpg" , face_img)
    
    temp_directory = "Temp"

    for student in os.listdir(db_directory):
        for face in os.listdir(temp_directory):
            print(f"compairing {student} with {face}")
            try:
                verification = DeepFace.verify(f"{db_directory}/{student}" , f"{temp_directory}/{face}")
                print(verification['verified'])
                if verification['verified']:
                    results[student] = "Present"
                    break
                else:
                    results[student] = "Absent"
            except Exception as e:
                results[student] = "Absent"
                pass


    for to_remove in os.listdir(temp_directory):
        os.remove(f"Temp/{to_remove}")

    return results

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("main.html")

@app.route('/login' ,methods = ['GET' , 'POST'])
def login():
    if request.method =='POST':
    
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = os.listdir('DATABASE/USERS')
        if username not in users:
                return render_template("login.html" ,Error = True , messege = "No Such User" )
            
        with open(f'DATABASE/USERS/{username}/userinfo.json' , 'r' ) as f:
            data = json.load(f)
            if(password != data['password']):
                return render_template("login.html" ,Error = True , messege = "Incorrect Password" )
            
        return redirect(f'/{username}')

    return render_template("login.html")

@app.route('/signup',methods = ['GET' , 'POST'])
def signup():
    if request.method =='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        
        if(password != password2):
            return render_template("signup.html", Error = True , messege = "Password Should Match")

        for name in os.listdir("DATABASE/USERS"):
            if(name == username):
                return render_template("signup.html", Error = True , messege = "Username already taken")
        
        
        os.mkdir(f"DATABASE/USERS/{username.lower()}")
        
        info_data = {
            "username": username,
            "password": password, 
        }

        with open(os.path.join(f"DATABASE/USERS/{username}", "userinfo.json"), "w") as info_file:
            json.dump(info_data, info_file, indent=4)

        return redirect(f'/{username}')


            
    return render_template("signup.html" , Error  =False )



@app.route('/<string:username>')
def dashboard(username):
    users =os.listdir('DATABASE/USERS')
    if username not in users:
        return redirect('login')


    return render_template("dashboard.html",username = username)

@app.route('/<string:username>/new', methods=['GET', 'POST'])
def new(username):
    if(request.method =="POST"):
        class_name = request.form.get("class-name")
        branch = request.form.get("branch")
        start = request.form.get("sd")
        end = request.form.get("ed")
        
        
        folder_name = class_name.replace(" ","_")
        folder_path = os.path.join("DATABASE", folder_name)
        os.mkdir(folder_path)

        info_data = {
            "class_info": {
                "class_name": class_name,
                "branch": branch,
                "startdate": start,
                "enddate": end,
                "num_students":0
            },
            "students": []  
        }
    
        
        with open(os.path.join(folder_path, "info.json"), "w") as info_file:
            json.dump(info_data, info_file, indent=4)

        return redirect(f'{username}/classes')
    return render_template("new.html" , username = username)

@app.route('/<string:username>/classes')
def classes(username):
    database_dir = 'DATABASE'
    class_info = []

    for folder_name in os.listdir(database_dir):
        folder_path = os.path.join(database_dir, folder_name)

        if os.path.isdir(folder_path):
            info_path = os.path.join(folder_path, 'info.json')

            if os.path.exists(info_path):
                with open(info_path, 'r') as info_file:
                    info_data = json.load(info_file)
                    class_info.append(info_data)
        
    return render_template("classes.html" , class_info=class_info , username = username)

@app.route('/<string:username>/classes/<string:class_name>')
def classname(username , class_name):
    with open(f'DATABASE/{class_name}/info.json', 'r') as f:
        data = json.load(f)
    students = data['students']

    return render_template("class.html" , class_name=class_name , students = students , username=username)

@app.route('/<string:username>/classes/<string:class_name>/add_student' ,  methods=['GET', 'POST'])
def student(username , class_name):
    if request.method=="POST":
        firstname = request.form.get("first_name")
        lastname = request.form.get("last_name")
        email = request.form.get("email")
        roll = request.form.get("roll_number")
        gender = request.form.get("gender")
        file = request.files.get('photo')

        directory_path = f'DATABASE/{class_name}/IMAGES'

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        file.save(os.path.join(directory_path, firstname+".png"))


        with open(f'DATABASE/{class_name}/info.json', 'r') as f:
            data = json.load(f)

        new_student = {
            "full_name":firstname + " " +lastname,
            "email": email,
            "roll_number": roll,
            "gender": gender,
            "photo": firstname + ".png"
        }

        data['students'].append(new_student)
        data['class_info']['num_students'] = len(data['students'])

        with open(f'DATABASE/{class_name}/info.json', 'w') as f:
            json.dump(data, f, indent=4)

        

        return redirect(f'/{username}/classes/{class_name}' )

    return render_template("student.html" , class_name=class_name , username=username)

@app.route('/<string:username>/attendance')
def select(username):
    database_dir = 'DATABASE'
    class_info = []

    for folder_name in os.listdir(database_dir):
        folder_path = os.path.join(database_dir, folder_name)

        if os.path.isdir(folder_path):
            info_path = os.path.join(folder_path, 'info.json')

            if os.path.exists(info_path):
                with open(info_path, 'r') as info_file:
                    info_data = json.load(info_file)
                    class_info.append(info_data)
                    
    return render_template("select.html", class_info=class_info , username = username)

@app.route('/<string:username>/attendance/<string:class_name>' ,methods = ['GET' , 'POST'])
def attendance(username, class_name):
    submitted = False
    if request.method =="POST":

        submitted = True
        photo = request.files.get('classphoto')
        photo_path = 'static/IMG/temp.png'
        photo.save(photo_path)

        modified_image = mark_faces(photo_path)
        cv2.imwrite('static/IMG/output.jpeg' , modified_image)

        with open(f'DATABASE/{class_name}/info.json', 'r') as f:
            data = json.load(f)
        students = data['students']

        for student in students:
            im = cv2.imread(f"DATABASE/{class_name}/IMAGES/{student['photo']}")
            cv2.imwrite(f"static/IMG/Temp/{student['photo']}", im)

        results = compair_faces(f"DATABASE/{class_name}/IMAGES" , 'static/IMG/temp.png')

        return render_template("attendance.html" , class_name=class_name  , submitted =submitted , students = students , results=results , username=username)

    return render_template("attendance.html" , class_name=class_name , submitted = submitted , username= username)





if __name__ == "__main__":
    app.run(debug=True)

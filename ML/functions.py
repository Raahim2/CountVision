
import cv2
from deepface import DeepFace

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



@app.route('/attendance/<string:class_name>' ,methods = ['GET' , 'POST'])
def attendance(class_name):
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

        return render_template("attendance.html" , class_name=class_name  , submitted =submitted , students = students , results=results)

    return render_template("attendance.html" , class_name=class_name , submitted = submitted )


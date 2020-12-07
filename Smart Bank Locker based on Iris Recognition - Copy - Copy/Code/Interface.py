from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import filedialog
import os
import glob
from iris_recognition import Iris_Recognition
from database import Database
import shutil
import pickle

iris_obj = Iris_Recognition()
db = Database()


root = Tk(className="Iris recognizer")
root.title("X Bank")
root.geometry("900x900")
root.resizable(0,0)
# root.configure(bg="#4271B7")
root.update()


def raise_frame(frame):
    frame.tkraise()

def close():
    root.destroy()

# profile_picture = ''
# def upload_pic():
#     global profile_picture
#     profile_picture = filedialog.askopenfilename(initialdir="./", title="Select a File", filetypes=(("JPG files","*.JPG*"),("all files", "*.*")))
#     if not profile_picture:
#         profile_label.configure(text='file not Selected')
#     else:
#         profile_label.configure(text='Selected')
manager_iris_image1 = ''
def manager_upload_iris1():
    global manager_iris_image1
    manager_iris_image1 = filedialog.askopenfilename(initialdir="./", title="Select a File", filetypes=(("JPG files","*.JPG*"),("all files", "*.*")))
    if not manager_iris_image1:
        manager_iris1_label.configure(text='file not Selected')
    else:
        manager_iris1_label.configure(text='Selected')

manager_iris_image2 = ''
def manager_upload_iris2():
    global manager_iris_image2
    manager_iris_image2 = filedialog.askopenfilename(initialdir="./", title="Select a File", filetypes=(("JPG files","*.JPG*"),("all files", "*.*")))
    if not manager_iris_image2:
        manager_iris2_label.configure(text='file not Selected')
    else:
        manager_iris2_label.configure(text='Selected')

customer_iris_image1 = ''
def customer_upload_iris1():
    global customer_iris_image1
    customer_iris_image1 = filedialog.askopenfilename(initialdir="./", title="Select a File", filetypes=(("JPG files","*.JPG*"),("all files", "*.*")))
    if not customer_iris_image1:
        customer_iris1_label.configure(text='file not selected')
    else:
        customer_iris1_label.configure(text='Selected')


customer_iris_image2 = ''
def customer_upload_iris2():
    global customer_iris_image2
    customer_iris_image2 = filedialog.askopenfilename(initialdir="./", title="Select a File", filetypes=(("JPG files","*.JPG*"),("all files", "*.*")))
    if not customer_iris_image2:
        customer_iris2_label.configure(text='file not selected')
    else:
        customer_iris2_label.configure(text='Selected')

def recognize_iris(img):
    crop,r = iris_obj.localize_iris(img)
    normalized = iris_obj.normalize_iris(crop,60,300,r,100)
    encoded = iris_obj.encode_features(normalized)
    return encoded

def save_manager():
    global manager_iris_image1
    global manager_iris_image2
    existing_irises = []
    if os.path.isfile('./db.pkl'):
        data = db.read()
        for mkey in data.keys():
            for iris in data[mkey]['iris']:
                existing_irises.append(iris)
    
    if manager_name_entry.get() == '' or manager_cnic_entry.get() == '' or manager_iris_image1 == '':
        messagebox.showerror('Error','Please provide the required data to register.')
    else:
        yes = False
        for i in [manager_iris_image1, manager_iris_image2]:
            check, img = iris_obj.match_iris(recognize_iris(i), existing_irises)
            if check:
                yes = True
                break
        if yes:
            messagebox.showerror('Error', 'This user already exists.')
        else:
            if messagebox.showinfo('Info', 'Your account has been created! \n Please Log In.'):
                db.write(manager_name_entry.get(),manager_cnic_entry.get(),recognize_iris(manager_iris_image1),recognize_iris(manager_iris_image2))
                raise_frame(home)
            # manager_name.configure(text='Bank Manager ('+manager_name_entry.get()+') is signedIn')
            # manager_name2.configure(text='Bank Manager ('+manager_name_entry.get()+') is signedIn')
            # manager_name3.configure(text='Bank Manager ('+manager_name_entry.get()+') is signedIn')
        manager_name_entry.delete(0, END)
        manager_cnic_entry.delete(0, END)
        manager_iris_image1 = ''
        manager_iris_image2 = ''
        manager_iris1_label.configure(text='')
        manager_iris2_label.configure(text='')
        

login_manager_iris = ''
imglbl = ''
def login_manager_iris_upload():
    global login_manager_iris
    login_manager_iris = filedialog.askopenfilename(initialdir="./", title="Select a File", filetypes=(("JPG files","*.JPG*"),("all files", "*.*")))
    print(login_manager_iris)

    crop, r = iris_obj.localize_iris(login_manager_iris)
    img = Image.fromarray(crop, 'RGB')
    render = ImageTk.PhotoImage(img)
    global imglbl
    imglbl = Label(manager_login, image=render)
    imglbl.image = render
    imglbl.grid(row=1,rowspan=3,column=2 ,padx=0,pady=0)

manager = ''
def login_manager():
    if login_manager_iris != '':
        global imglbl
        if os.path.isfile('./db.pkl'):
            data = db.read()
            irises = list()
            for key in data.keys():
                for iris in data[key]['iris']:
                    irises.append(iris)
            check, img = iris_obj.match_iris(recognize_iris(login_manager_iris), irises)
            if check:
                global manager
                # user = ''
                for key in data.keys():
                    for val in data[key]['iris']:
                        if (img == val).all():
                            manager = key
                            break
                manager_name.configure(text='Bank Manager ('+data[manager]['name']+') is SignedIn')
                raise_frame(manager_page)
                imglbl.image = None
            else:
                imglbl.image = None
                messagebox.showerror("Error", "Invalid iris \nPlease try agian.")
                
        else:
            imglbl.image = None
            messagebox.showerror("Error", "You are not registered")
    else:
        messagebox.showerror('Error', 'Please provide the required data.')
        

def logout_manager():
    raise_frame(home)

locker = 0
def save_customer():
    global customer_iris_image1
    global customer_iris_image2
    if customer_name_entry.get() == '' or customer_cnic_entry.get() == '' or customer_iris_image1 == '':
        messagebox.showerror('Error', 'Please provide the required data to register.')
    else:
        global locker
        locker += 1
        data = db.read()
        irises = []
        existing_irises = []
        # getting existing irises
        for mkey in data.keys():
            if data[mkey]['customers'].keys():
                for ckey in data[mkey]['customers'].keys():
                    for iris in data[mkey]['customers'][ckey]['iris']:
                        existing_irises.append(iris)
            else:
                break
        # checking if new iris already exists
        iris_exists = False
        for i in [customer_iris_image1,customer_iris_image2]:
            if i != '':
                check,img = iris_obj.match_iris(recognize_iris(i), existing_irises)
                if check:
                    iris_exists = True
                else:
                    irises.append(recognize_iris(i).ravel()) 
        if iris_exists:
            messagebox.showerror("Error", "This user already exists.")
        else:
            username = customer_name_entry.get()
            username = username.replace(" ","")
            for mkey in data.keys():       
                if username not in data[mkey]['customers'].keys():
                    data[mkey]['customers'][username] = {
                        'name':customer_name_entry.get(),
                        'cnic':customer_cnic_entry.get(),
                        'locker':locker,
                        'iris':irises
                    }
            if messagebox.showinfo('Info', 'Your account has been created! \n Please Log In.'):
                with open('./db.pkl','wb') as book:
                    pickle.dump(data, book)
                raise_frame(manager_page)
        
        customer_name_entry.delete(0, END)
        customer_cnic_entry.delete(0, END)
        customer_iris_image1 = ''
        customer_iris_image2 = ''
        customer_iris1_label.configure(text='')
        customer_iris2_label.configure(text='')
    


login_customer_iris = ''
customerloginImglbl = ''
def login_customer_iris_upload():
    global customerloginImglbl
    global login_customer_iris
    login_customer_iris = filedialog.askopenfilename(initialdir="./", title="Select a File", filetypes=(("JPG files","*.JPG*"),("all files", "*.*")))
    print(login_customer_iris)

    crop, r = iris_obj.localize_iris(login_customer_iris)
    img = Image.fromarray(crop, 'RGB')
    render = ImageTk.PhotoImage(img)
    global customerloginImglbl
    customerloginImglbl = Label(customer_login, image=render)
    customerloginImglbl.image = render
    customerloginImglbl.grid(row=1,rowspan=3,column=2 ,padx=0,pady=0)


customer = ''
manager_customer = ''
def login_customer():
    global login_customer_iris
    if login_customer_iris != '':
        global customerloginImglbl
        data = db.read()
        irises = list()
        for mkey in data.keys():
            for ckey in data[mkey]['customers'].keys():
                for iris in data[mkey]['customers'][ckey]['iris']:
                    irises.append(iris)
        check, img = iris_obj.match_iris(recognize_iris(login_customer_iris), irises)
        if check:
            global customer
            # user = ''
            for mkey in data.keys():
                for ckey in data[mkey]['customers'].keys():
                    for val in data[mkey]['customers'][ckey]['iris']:
                        if (img == val).all():
                            customer = ckey
                            manager_customer = mkey

            customer_name.configure(text=''+data[manager_customer]['customers'][customer]['name']+' Locker is opened')
            customer_locker_num.configure(text='Locker number: '+str(data[manager_customer]['customers'][customer]['locker'])+' ')
            raise_frame(customer_page)
            customerloginImglbl.image = None
        else:
            customerloginImglbl.image = None
            messagebox.showerror("Error", "Invalid iris \nPlease try agian.") 
    else:
        messagebox.showerror('Error','Please provide the required data.')

def logout_customer():
    raise_frame(manager_page)


#header
img1 = ImageTk.PhotoImage(Image.open("btn\lego.png"))
panel1= Label(root, bg="white",width=250,height=15).grid(row=0, column=0, sticky='ew')
Label(panel1,image=img1,bg="white" ,width=200,height=200).place(x=200,y=10)
Label(panel1,text="Smart Bank Locker ",bg="white",fg="#00ABD2",font=("Helvetica",30)).place(x=350,y=130)

home = Frame(root, width=700)
manager_login = Frame(root)
manager_register = Frame(root)
manager_page = Frame(root)
customer_login = Frame(root)
customer_register = Frame(root)
customer_page = Frame(root)

for frame in (home,manager_login,manager_register,manager_page,customer_login,customer_register, customer_page):
    frame.grid(row=1, column=0, padx=00, pady=10,sticky='nesw',rowspan=2)

# home page

mang_in = ImageTk.PhotoImage( Image.open("btn\mang_in.png"))
mang_reg=ImageTk.PhotoImage( Image.open("btn\mang_reg.png"))
quit=ImageTk.PhotoImage( Image.open("btn\quit.png"))

Label(home, text='Welcome to smart bank locker',fg="black",font=("Helvetica",20)).grid(row=0,padx=300,pady=5)
Button(home,text="login Bank Manager",  image=mang_in,border=0,bg="#F1F0F0",width=400 ,command=lambda:raise_frame(manager_login)).grid(row=1,pady=10)
Button(home, text="Register Bank Manager",image=mang_reg,border=0,bg="#F1F0F0",width=400 , command=lambda:raise_frame(manager_register)).grid(row=2,pady=0)
Button(home, text="Close",image=quit,border=0,bg="#F1F0F0",width=400  ,command=close).grid(row=3,pady=10)


#manager login page
scan=ImageTk.PhotoImage( Image.open("btn\scan.png"))
Oroom=ImageTk.PhotoImage( Image.open("btn\Oroom.png"))
Croom=ImageTk.PhotoImage( Image.open("btn\Croom.png"))
back=ImageTk.PhotoImage( Image.open("btn\_back.png"))
register=ImageTk.PhotoImage( Image.open("btn\_register.png"))

Label(manager_login, text='Bank Manager Login',font=("Helvetica",20)).grid(row=0,column=1,columnspan=2,padx=100,pady=0)
Button(manager_login, text='Please use iris image', image=scan,border=0,bg="#F1F0F0",width=250 ,command=login_manager_iris_upload).grid(row=1,padx=50,pady=15)
Button(manager_login, text='LogIn', image=Oroom,border=0,bg="#F1F0F0",width=250,command=login_manager).grid(row=2,column=0,padx=1,pady=0)
Button(manager_login, image=back,border=0,bg="#F1F0F0",width=250, command=lambda: raise_frame(home)).grid(row=3,column=0,padx=1,pady=25)

#manager registeration page
iris1=ImageTk.PhotoImage( Image.open("btn\iris1.png"))
iris2=ImageTk.PhotoImage( Image.open("btn\iris2.png"))

Label(manager_register, text='Bank Manager Register', font=("roboto",20)).grid(row=0,padx=300,pady=5)

Label(manager_register, text='Name:', width=21,fg="#5BAADE",font=("roboto",15)).place(x=120,y=60)
manager_name_entry = Entry(manager_register,width=21,bg="#9AAF9A", font=("roboto",15))
manager_name_entry.place(x=130,y=100)

Label(manager_register, text="Enter CNIC:",width=21, fg="#5BAADE",font=('roboto',15)).place(x=500,y=60)
manager_cnic_entry = Entry(manager_register, width=21,bg="#9AAF9A",border=1, font=("roboto",15))
manager_cnic_entry.place(x=500,y=100)

iris_img1 = Button(manager_register,image=iris1,border=0,bg="#F1F0F0",width=250,command=manager_upload_iris1).place(x=120,y=180)
manager_iris1_label = Label(manager_register, text='', font=("Courier",12), )
manager_iris1_label.place(x=370, y=200)

manageriris_img2 = Button(manager_register,image=iris2,border=0,bg="#F1F0F0",width=250, command=manager_upload_iris2).place(x=490,y=180)
manager_iris2_label = Label(manager_register, text='', font=("Courier",12), )
manager_iris2_label.place(x=740, y=200)

Button(manager_register, text='Back',image=back,border=0,bg="#F1F0F0",width=250, command=lambda: raise_frame(home)).place(x=490,y=270)
Button(manager_register, text='Register',image=register,border=0,bg="#F1F0F0",width=250,command=save_manager).place(x=120,y=270)

#manager home page
userRegister=ImageTk.PhotoImage( Image.open("btn\_userRegister.png"))
userSign=ImageTk.PhotoImage( Image.open("btn\_userSign.png"))
logout=ImageTk.PhotoImage( Image.open("btn\logout.png"))

manager_name = Label(manager_page, text='', font=("roboto",20))
manager_name.place(x=220, y=0)
Label(manager_page, text='Bank Locker User Window', font=("roboto", 20)).place(x=290, y=40)
Button(manager_page, text='Login Locker User', image=userSign,width=250, border=0, command=lambda:raise_frame(customer_login)).place(x=310,y=90)
Button(manager_page, text='Register Locker User', image=userRegister, width=250,border=0 ,command=lambda:raise_frame(customer_register)).place(x=310, y=160)
Button(manager_page, text='Logout',image=Croom, width=250,border=0, command=logout_manager).place(x=310,y=270)

#customer register page

# manager_name2 = Label(customer_register, text='', font=("Courier",20))
# manager_name2.place(x=50, y=100)
Label(customer_register, text='Bank Locker User Registration', font=("roboto",20)).grid(row=0,padx=300,pady=5)

Label(customer_register, text='Enter Name:', width=21,fg="#5BAADE",font=("roboto",15)).place(x=120,y=60)
customer_name_entry = Entry(customer_register,width=21,bg="#9AAF9A", font=("roboto",15))
customer_name_entry.place(x=130,y=100)

Label(customer_register, text="Enter CNIC:",width=21, fg="#5BAADE",font=('roboto',15)).place(x=500,y=60)
customer_cnic_entry = Entry(customer_register, width=21,bg="#9AAF9A",border=1, font=("roboto",15))
customer_cnic_entry.place(x=500,y=100)

customer_iris_img1 = Button(customer_register,image=iris1,border=0,bg="#F1F0F0",width=250,command=customer_upload_iris1).place(x=120,y=180)
customer_iris1_label = Label(customer_register, text='', font=("Courier",12) )
customer_iris1_label.place(x=370, y=200)

customer_iris_img2 = Button(customer_register,image=iris2,border=0,bg="#F1F0F0",width=250, command=customer_upload_iris2).place(x=490,y=180)
customer_iris2_label = Label(customer_register, text='', font=("Courier",12), )
customer_iris2_label.place(x=740, y=200)

Button(customer_register, text='Back', image=back,border=0,bg="#F1F0F0",width=250, command=lambda: raise_frame(manager_page)).place(x=490,y=270)
Button(customer_register, text='Register',image=register,border=0,bg="#F1F0F0",width=250,command=save_customer).place(x=120,y=270)


# customer login page

# manager_name3 = Label(customer_login, text='', font=("Courier",20))
# manager_name3.place(x=50, y=100)

Olocker=ImageTk.PhotoImage( Image.open("btn\Olocker.png"))
Clocker=ImageTk.PhotoImage( Image.open("btn\Clocker.png"))

Label(customer_login, text='Bank Locker User Login',font=("Helvetica",20)).grid(row=0,column=1,columnspan=2,padx=100,pady=0)
Button(customer_login, text='Please use iris image', image=scan,border=0,bg="#F1F0F0",width=250,command=login_customer_iris_upload).grid(row=1,padx=50,pady=15)
Button(customer_login, text='Back',  image=back,border=0,bg="#F1F0F0",width=250, command=lambda: raise_frame(manager_page)).grid(row=3,column=0,padx=1,pady=25)
Button(customer_login, text='LogIn', image=Olocker,border=0,bg="#F1F0F0",width=250,command=login_customer).grid(row=2,column=0,padx=1,pady=0)

# customer home page
Clocker=ImageTk.PhotoImage( Image.open("btn\Clocker.png"))

Label(customer_page, text='Welcome to Smart Bank Locker', fg="#67BF6A",font=("Helvetica",20)).grid(row=0,column=0,padx=0,pady=0)
customer_name = Label(customer_page, text='',fg="#5BAADE", font=("Helvetica",20))
customer_name.grid(row=1,column=0,padx=0,pady=10)
customer_locker_num = Label(customer_page, text='', font=("Helvetica",20))
customer_locker_num.grid(row=2,column=0,padx=0,pady=5)

lockers = ImageTk.PhotoImage(Image.open("btn\loc.png"))
Label(customer_page,image=lockers,bg="white" ,width=372,height=318).grid(row=0,column=1, rowspan=4,padx=70,pady=30 )




Button(customer_page, text='Logout', image=Clocker,border=0,bg="#F1F0F0",width=250, command=logout_customer).grid(row=3,column=0,padx=0,pady=30)





raise_frame(home)

root.mainloop()
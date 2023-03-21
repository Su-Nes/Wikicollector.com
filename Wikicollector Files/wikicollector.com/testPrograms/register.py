from email_validator import validate_email, EmailNotValidError

registrants = {} #pagaidām lieku user datus (vārdu un uzvārdu) dictionary, vēlāk pārlikšu uz datubāzi

class Register:
    def __init__(self, email, password, name, surname):
        self.email = email
        self.password = password
        self.name = name
        self.surname = surname

    def Save(self):
        try:    #verificē epastu
            validation = validate_email(self.email)
            self.email = validation.email

            if len(self.name) < 3 or len(self.name) > 50:   #pārbaudīt, vai vārds nav pa īsu va pa garu
                print("Name invalid\n")
            else:
                registrants[self.name] = self.surname
                print("Save successful!\n")
        except EmailNotValidError as e: #izmet kļūdu, ja epasts neeksistē
            print(str(e))

    def userInfo(self):
        return self.email + ", " + self.password + ", " + self.name + ", " + self.surname

newUser = Register("jrozentāls@gmail.com", "landscape123", "Jānis", "Rozentāls")
newUser.Save()
print(newUser.userInfo())

newUser1 = Register("nav_epasts", "parole123", "Kārlis", "Suneps") #nepareiza epasta formāta reģistrants
newUser1.Save()


print("\n", registrants)
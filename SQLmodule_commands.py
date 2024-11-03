from sqlmodel import SQLModel, Field, create_engine, Session, select, delete
from datetime import datetime
from sqlalchemy import text
import streamlit as st

# SQLModel-Datenbankverbindung
sqlite_url = "sqlite:///users.db"
engine = create_engine(sqlite_url)

# --- Daten-Tabellen ---

# Tabelle für erlaubte Matrikelnummern für whitelisting
class ErlaubteMatrikelnummern(SQLModel, table=True):
    __tablename__ = "erlaubtematrikelnummern"
    __table_args__ = {'extend_existing': True}
    alle_matrikelnummern: str = Field(primary_key=True, nullable=False) 
    unregistrierten_matrikelnummern: str

# Tabelle für Benutzerdaten für die Authentifizierung
class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}
    matrikelnummern: str = Field(primary_key=True, nullable=False)
    vorname: str = Field(nullable=False)
    nachname: str = Field(nullable=False)
    email: str = Field(nullable=False)
    passwort: str = Field(nullable=False)
    admin: bool = Field(default=False)

# Tabelle für Vorlesungen für Multiple-Choice-Fragen
class Lecture(SQLModel, table=True):
    __tablename__ = "lecture"
    __table_args__ = {'extend_existing': True}
    id: int = Field(primary_key=True, nullable=False)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)

# Tabelle für Multiple-Choice-Fragen
class MTL_Question(SQLModel, table=True):
    __tablename__ = "mtl_question"
    __table_args__ = {'extend_existing': True}
    id: int = Field(primary_key=True, nullable=False)
    lecture_id: int = Field(foreign_key="lecture.id", nullable=False)
    question_text: str = Field(nullable=False)
    options_1: str
    options_2: str
    options_3: str
    options_4: str
    answer: str = Field(nullable=False)

# Tabelle für Benutzerfortschritt bei Multiple-Choice-Fragen
class UserProgress(SQLModel, table=True):
    __tablename__ = "userprogress"
    __table_args__ = {'extend_existing': True}
    id: int = Field(primary_key=True, nullable=False)
    matrikelnummern: str = Field(foreign_key="user.matrikelnummern", nullable=False)
    lecture_id: int = Field(foreign_key="lecture.id", nullable=False)
    question_id: int = Field(foreign_key="mtl_question.id")
    correct_count: int = Field(default=0, nullable=False)
    last_answered: datetime = Field(default_factory=datetime.now)

# Funktion zum Erstellen der Tabellen in der Datenbank
def create_tables():
    SQLModel.metadata.create_all(engine, checkfirst=True)
    print("Tabellen wurden erfolgreich erstellt")  # Debugging-Zwecke

# Falls eine tabelle zu viel erstellt wurde, kann diese Funktion verwendet werden, um die Tabelle zu löschen
def drop_table():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS question"))
        conn.commit()
    print("Tabelle 'question' wurde erfolgreich gelöscht.")

# --- Authentifizierung-Operationen ---
# Überprüfen, ob User exitiert und ob die anmelde Daten korrekt sind
def login_check(matrikelnummern, passwort):
    with Session(engine) as session:
        # Suche nach dem Benutzer mit der angegebenen Matrikelnummer
        user = session.exec(select(User).where(User.matrikelnummern == matrikelnummern)).first()
        if user:
            # Passwortüberprüfung
            if user.passwort == passwort:
                return True
            else:
                #st.toast("Passwort ist falsch", icon='❌')
                st.error("Passwort ist falsch", icon='❌')
                return False
        else:
            #st.toast(f"{matrikelnummern} ist nicht zu einem existierenden Account registriert", icon='❌')
            st.error(f"{matrikelnummern} ist nicht zu einem existierenden Account registriert", icon='❌')
            return False

# Funktion, um einen neuen Benutzer hinzuzufügen oder zu aktualisieren
def add_user(matrikelnummern, vorname, nachname, email, passwort, admin=False):
    with Session(engine) as session:
        # Verwende die Funktion "get_registered_user_ids", um die Matrikelnummern der registrierten Benutzer abzurufen
        registered_users = get_registered_user_ids()
         # Überprüfen, ob die Matrikelnummer bereits registriert ist
        if matrikelnummern in registered_users:
            #st.toast(f"{matrikelnummern} ist bereits registriert", icon='❌')
            st.error(f"{matrikelnummern} ist bereits registriert", icon='❌')
            return False
            if not matrikelnummern in get_allowed_matrikelnummern():
                #st.toast(f"{matrikelnummern} steht nicht auf der Whitelist und darf deswegen nicht registriert werden", icon='❌')
                st.error(f"{matrikelnummern} steht nicht auf der Whitelist und darf deswegen nicht registriert werden", icon='❌')
                return False
            else:
                new_user = User(matrikelnummern=matrikelnummern, vorname=vorname, nachname=nachname, email=email, passwort=passwort, admin=admin)
                delelte_unregister_matrikelnummer = session.exec(delete(ErlaubteMatrikelnummern).where(ErlaubteMatrikelnummern.alle_matrikelnummern == matrikelnummern))
                session.add(new_user)
                session.commit()
                return True

# --- Admin-Operationen ---
# Hinzufügen eines Benutzers durch den Admin (mehr flexibilität und Controlle als bei der normalen Registrierung)
def add_user_in_admin(matrikelnummern, vorname, nachname, email, passwort, is_user_admin):
    with Session(engine) as session:
        # Verwende die Funktion "get_registered_user_ids", um die Matrikelnummern der registrierten Benutzer abzurufen
        registered_users = get_registered_user_ids()
        # Überprüfen, ob die Matrikelnummer bereits registriert ist
        if matrikelnummern in registered_users:
            #st.toast(f"{matrikelnummern} ist bereits registriert", icon='❌')
            st.error(f"{matrikelnummern} ist bereits registriert", icon='❌')
            return False
        else:
            new_allowed_matrikelnummern = ErlaubteMatrikelnummern(alle_matrikelnummern=matrikelnummern)
            new_user = User(matrikelnummern=matrikelnummern, vorname=vorname, nachname=nachname, email=email, passwort=passwort, admin=is_user_admin)
            session.add(new_user)
            session.commit()
            return True

# Sucht die Matrikelnummer der unregegistrierten und erlaubten Benutzer 
def get_unregistered_matrikelnummern():
    """
    Gibt eine Liste der unregistrierten Matrikelnummern zurück.
    """
    with Session(engine) as session:
        statement = select(ErlaubteMatrikelnummern.unregistrierten_matrikelnummern)
        unregistered_matrikelnummern = session.exec(statement).all()  # Verwende .all() direkt
    return unregistered_matrikelnummern

# Fügt Matrikelnummer zur Whitelist hinzu
def add_unregistered_matrikelnummern(matrikelnummer):
    """
    Fügt eine Matrikelnummer zur Tabelle hinzu, falls sie noch nicht in `alle_matrikelnummern` existiert.
    Matrikelnummer wird sowohl in `alle_matrikelnummern` als auch in `unregistrierten_matrikelnummern` eingetragen.
    """
    with Session(engine) as session:
        # Prüfe, ob die Matrikelnummer bereits genehmigt wurde
        vorhandene_matrikelnummer = session.exec(
            select(ErlaubteMatrikelnummern).where(ErlaubteMatrikelnummern.alle_matrikelnummern == matrikelnummer)
        ).first()
        
        if vorhandene_matrikelnummer:
            st.toast(f"Matrikelnummer {matrikelnummer} ist bereits genehmigt", icon='❌')
        else:
            # Neue Zeile mit Matrikelnummer in beiden Spalten hinzufügen
            neue_matrikelnummer = ErlaubteMatrikelnummern(
                alle_matrikelnummern=matrikelnummer, 
                unregistrierten_matrikelnummern=matrikelnummer
            )
            session.add(neue_matrikelnummer)
            try:
                session.commit()
                st.toast(f"Matrikelnummer {matrikelnummer} erfolgreich zur Erlaubtenliste hinzugefügt", icon='✅')
            except IntegrityError as e:
                session.rollback()
                st.error(f"Fehler beim Einfügen: {e}")

# Löscht Matrikelnummer aus der Whitelist
def delete_erlaubte_matrikelnummer(matrikelnummer):
    with Session(engine) as session:
        statement = delete(ErlaubteMatrikelnummern).where(ErlaubteMatrikelnummern.alle_matrikelnummern == matrikelnummer)
        session.exec(statement)
        session.commit()

# Gibt alle erlaubten Matrikelnummern zurück
def get_allowed_matrikelnummern():
    with Session(engine) as session:
        statement = select(ErlaubteMatrikelnummern.alle_matrikelnummern)
        users = session.exec(statement).all()
    return users

# Ruft alle registrierten Benutzer-Matrikelnummern auf
def get_registered_user_ids():
    with Session(engine) as session:
        # Rückgabe der Matrikelnummern als einfache Liste
        statement = select(User.matrikelnummern)
        users = session.exec(statement).all()  # Verwende nur .all() ohne .scalars()
    return users

# Überprüft ob der eingeloggt Benutzer Admin ist
def is_user_admin(matrikelnummern):
    with Session(engine) as session:
        #Die Matrikelnummer wird überprüft
        user = session.exec(select(User).where(User.matrikelnummern == matrikelnummern)).first()
        #Wenn der Benutzer ein Admin ist, wird True zurückgegeben
        if user.admin:
            return True
        else:
            return False

# Alle Informationen über den Benutzer werden zurückgegeben
def get_all_users_info():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
    return users

# Alle User Daten können bearbeitet werden
def update_all_users_info(matrikelnummern, vorname=None, nachname=None, email=None, passwort=None, admin=None):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.matrikelnummern == matrikelnummern)).first()
        if user:
            if vorname: user.vorname = vorname
            if nachname: user.nachname = nachname
            if email: user.email = email
            if passwort: user.passwort = passwort
            if admin is not None: user.admin = admin
            session.commit()

# Löscht den Benutzer
def delete_user_completly(matrikelnummern):
    with Session(engine) as session:
        statement = delete(User).where(User.matrikelnummern == matrikelnummern)
        session.exec(statement)
        session.commit()

# Gibt alle Vorlesungsinformation zurück
def get_all_lectures():
    with Session(engine) as session:
        lectures = session.exec(select(Lecture)).all()
    return lectures

# Fügt eine neue Vorlesung hinzu 
def add_lecture(title, description):
    with Session(engine) as session:
        new_lecture = Lecture(title=title, description=description)
        session.add(new_lecture)
        session.commit()

# Updated eine Vorlesung
def update_lecture(lecture_id, title=None, description=None):
    with Session(engine) as session:
        lecture = session.exec(select(Lecture).where(Lecture.id == lecture_id)).first()
        if lecture:
            if title: lecture.title = title
            if description: lecture.description = description
            session.commit()

# Löscht eine Vorlesung und alle verbunden Fragen in MTL_Question
def delete_lecture(lecture_titel):
    with Session(engine) as session:
        # Holt die Vorlesung
        lecture = session.exec(select(Lecture).where(Lecture.title == lecture_titel)).first()
        # Holt die ID der Vorlesung
        current_lecuture_id =session.exec(select(Lecture.id).where(Lecture.title == lecture_titel)).first()
        if lecture:
            # Löscht die Mutliple-Choice-Fragen die mit der Vorlesung verbunden sind
            mtl_question_statement = delete(MTL_Question).where(MTL_Question.lecture_id == current_lecuture_id.id)
            # Löscht die Vorlesung
            lecture_statement = delete(Lecture).where(Lecture.title == lecture_titel)
            session.exec(statement)
            session.commit()

# Gibt alle Multiple-Choice-Fragen zurück
def get_all_mtl_questions():
    with Session(engine) as session:
        questions = session.exec(select(MTL_Question)).all()
    return questions

# Fügt alle Multiple-Choice-Fragen hinzu
def add_mtl_question(lecture_titel, question_text, options_1, options_2, options_3, options_4, answer):
    with Session(engine) as session:
        current_lecuture_id =session.exec(select(Lecture.id).where(Lecture.title == lecture_titel)).first()
        new_question = MTL_Question(
            lecture_id=current_lecuture_id,
            question_text=question_text,
            options_1=options_1,
            options_2=options_2,
            options_3=options_3,
            options_4=options_4,
            answer=answer
        )
        session.add(new_question)
        session.commit()
        st.toast("Frage Hinzu gefügt", icon='🎉')

# Updated Multiple-Choice-Frage
def update_mtl_question(question_id, lecture_id=None, question_text=None, options_1=None, options_2=None, options_3=None, options_4=None, answer=None):
    with Session(engine) as session:
        question = session.exec(select(MTL_Question).where(MTL_Question.id == question_id)).first()
        if question:
            if lecture_id: question.lecture_id = lecture_id
            if question_text: question.question_text = question_text
            if options_1: question.options_1 = options_1
            if options_2: question.options_2 = options_2
            if options_3: question.options_3 = options_3
            if options_4: question.options_4 = options_4
            if answer: question.answer = answer
            session.commit()

# Löscht Multiple-Choice-Frage
def delete_mtl_question(question_id):
    try:
        question_id = int(question_id)  # Stelle sicher, dass die ID als Integer vorliegt
    except ValueError:
        st.toast("Ungültige Frage-ID. Bitte geben Sie eine numerische ID ein.", icon='❌')
        return
    
    with Session(engine) as session:
        question = session.exec(select(MTL_Question).where(MTL_Question.id == question_id)).first()
        
        if question:
            session.delete(question)
            session.commit()
            st.toast(f"Frage mit der ID: {question_id} wurde erfolgreich gelöscht", icon="🗑️")
        else:
            st.toast("Diese Frage-ID existiert nicht", icon='❌')


# Ausgabe von Vor- und nachname des Benutzers
def get_user_full_name(matrikelnummern):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.matrikelnummern == matrikelnummern)).first()
        if user:
            return f"{user.vorname} {user.nachname}"
        else:
            return None





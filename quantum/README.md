# **ETSI-basiertes KME-Schlüsselmanagementsystem**

Ein Django-basiertes Schlüsselmanagementsystem, das Schlüsselgenerierung, -speicherung und -austausch gemäß der ETSI GS QKD 014 V1.1.1-Norm implementiert.

---

## **Features**

- **Schlüsselmanagement innerhalb eines KMEs:**
  - Registrierung und Authentifizierung von SAEs (Subscriber Authentication Entities) mit JWT-Token.
  - Generierung und Austausch von Schlüsseln zwischen SAE-Master und SAE-Slave.
- **Mehrere KMEs:**
  - Zertifikatsbasierte Authentifizierung zwischen KMEs.
  - Übertragung und Speicherung von Schlüsseln zwischen KMEs.
- **Sicherheitsmaßnahmen:**
  - TLS-gesicherte Kommunikation.
  - Speicherung verschlüsselter Schlüssel in der Datenbank.

---

## **Anforderungen**

### **Systemvoraussetzungen**

- Python 3.9 oder höher
- Django 4.x
- Abhängigkeiten (siehe [requirements.txt](requirements.txt))

### **Installationsanweisungen**

1. **Repository klonen:**
   ```bash
   git clone https://github.com/Steve2404/Quantum_API.git
   cd Quantum_API

2. **Virtuelle Umgebung erstellen und aktivieren:**
   ```bash
   python -m venv .env
   source .env/bin/activate    # Für Linux/MacOS
   .env\Scripts\activate       # Für Windows
   ```

3. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```
   
4. **Datenbank initialisieren:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Superuser erstellen (für die Verwaltung):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Server starten:**
   ```bash
   python manage.py runserver
   ```
---

### **API-Endpunkte**


### **Benutzerverwaltung**

1. **Registrierung**
   - **Route:** `/api/v1/register/`
   - **Methode:** POST
   - **Beschreibung:** Registriert einen Benutzer mit Benutzername und Passwort.

2. **Authentifizierung**
   - **Route:** `/api/v1/token/`
   - **Methode:** POST
   - **Beschreibung:** Generiert ein JWT-Token, um autorisierte Anfragen zu stellen.

---

### Teil 1: **Schlüsselmanagement innerhalb eines KME**

1. **Schlüsselgenerierung**
   - **Route:** `/api/v1/keys/{slave_SAE_ID}/enc_keys/`
   - **Methode:** POST
   - **Beschreibung:** Generiert Schlüssel für die angegebene SAE (Slave).
   - **Beispiel:**
     ```json
     {
       "master_sae_id": "master-uuid",
       "number": 5,
       "size": 128
     }
     ```
2. **Schlüsselabruf**
   - **Route:** `/api/v1/keys/{slave_SAE_ID}/enc_keys/`
   - **Methode:** GET
   - **Beschreibung:** Ruft die verschlüsselten Schlüssel ab.

3. **Schlüsselabruf (mit ID)**
   - **Route:** `/api/v1/keys/{master_SAE_ID}/dec_keys/`
   - **Methode:** GET
   - **Beschreibung:** Ruft einen spezifischen Schlüssel mit seiner ID ab.

4. **Statusprüfung**
   - **Route:** `/api/v1/keys/{slave_SAE_ID}/status/`
   - **Methode:** GET
   - **Beschreibung:** Prüft den Status einer SAE.

---

### Teil 2: **Schlüsselmanagement zwischen zwei KMEs**

1. **Zertifikatsprüfung**
   - **Route:** `/api/v1/certificates/validate/`
   - **Methode:** POST
   - **Beschreibung:** Validiert die Zertifikate zwischen zwei KMEs, um eine sichere Verbindung herzustellen.

2. **Schlüsselübertragung**
   - **Route:** `/api/v1/keys/transfer/`
   - **Methode:** POST
   - **Beschreibung:** Überträgt Schlüssel von einem KME zu einem anderen.
---

## **Testanweisungen**

1. **Postman-Konfiguration:**  
   - Importieren Sie die bereitgestellte Postman-Collection (falls vorhanden) oder konfigurieren Sie die Anfragen manuell.
   - Fügen Sie das JWT-Token im Header hinzu:
     ```http
     Authorization: Bearer <token>
     ```

2. **Beispielablauf:**
   - **Registrierung und Authentifizierung:**
     1. Benutzer registrieren über `/api/v1/register/`.
     2. Token abrufen über `/api/v1/token/`.

   - **Schlüssel generieren und abrufen:**
     1. Senden Sie eine POST-Anfrage an `/api/v1/keys/{slave_SAE_ID}/enc_keys/`.
     2. Rufen Sie die Schlüssel mit einer GET-Anfrage ab.

   - **Zertifikatsvalidierung und Schlüsselübertragung:**
     1. Zertifikate validieren über `/api/v1/certificates/validate/`.
     2. Schlüssel zwischen KMEs übertragen über `/api/v1/keys/transfer/`.



## **Zukünftige Arbeiten**

- Integration von physikalischen QKD-Systemen.
- Erweiterung der Zertifikatsverwaltung.
- Optimierung der Benutzeroberfläche und -erfahrung.






��          t      �             ,   *  {   W      �     �           $      E     f  0   �  k  �  �     )     v   G  '   �     �       0     '   P  "   x  <   �                            
          	                              Endpoint pour générer ou récupérer les clés (enc_keys).
        POST : Générer des clés (utilisé par le SAE maître).
        GET : Récupérer les clés générées (utilisé par le SAE esclave).
        https://{KME_hostname}/api/v1/keys/{slave_SAE_ID}/enc_keys  Modèle pour représenter une entité KME.  Endpoint pour récupérer le statut des clés pour un SAE esclave. https://{KME_hostname}/api/v1/keys/{slave_SAE_ID}/status KME not found for the Master SAE Master SAE ID not provided Master SAE not found No keys found for this Slave SAE No master SAE found for this KME Slave SAE or KME not found ViewSet pour gérer les requêtes liées au KME. Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2024-10-10 12:31+0200
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
 Endpunkt zum Generieren oder Abrufen von Schlüsseln (enc_keys).
 POST: Generieren von Schlüsseln (verwendet vom Master-SAE).
 GET: Abrufen der generierten Schlüssel (verwendet vom Slave-SAE).
 https://{KME_hostname}/api/v1/keys/{slave_SAE_ID}/enc_keys Modell zur Darstellung einer KME-Entität Endpunkt zum Abrufen des Schlüsselstatus für ein Slave-SAE. https://{KME_hostname}/api/v1/keys/{slave_SAE_ID}/status KME nicht gefunden für den Master-SAE. Master-SAE-ID nicht angegeben Master-SAE nicht gefunden. Keine Schlüssel für diesen Slave-SAE gefunden. Kein Master-SAE für diese KME gefunden Slave-SAE oder KME nicht gefunden. ViewSet zur Verwaltung von Anfragen im Zusammenhang mit KME. 

# API REST - Gestion d'Événements (FastAPI + SQLite)

Cette API permet de gérer des événements avec des catégories, en lecture, création, modification et suppression.

## Endpoints

### 1. `GET /events/`

- **Description** : Récupère tous les événements avec leurs détails.
- **Réponse** : Liste d’événements au format JSON.
- **Code HTTP** : `200 OK`

---

### 2. `GET /events/{event_id}`

- **Description** : Récupère un événement spécifique par son identifiant.
- **Paramètre** :
  - `event_id` (int) – identifiant de l’événement
- **Réponse** :
  - Succès : objet JSON de l’événement
  - Échec : `{"detail": "NOT_FOUND"}`
- **Code HTTP** : `200 OK` ou `404 Not Found`

---

### 3. `POST /events/create`

- **Description** : Crée un nouvel événement avec des catégories optionnelles.
- **Corps de la requête** : un objet `Event` en JSON (voir schéma ci-dessous).
- **Réponse** : message de confirmation avec l’identifiant.
- **Code HTTP** : `201 Created`

---

### 4. `PUT /events/{event_id}`

- **Description** : Met à jour un événement existant.
- **Paramètre** : `event_id` (int)
- **Corps** : objet `Event` modifié en JSON.
- **Réponse** :
  - Succès : message de confirmation
  - Échec : `{"detail": "NOT_FOUND"}`
- **Code HTTP** : `200 OK` ou `404 Not Found`

---

### 5. `DELETE /events/{event_id}`

- **Description** : Supprime un événement et ses associations de catégories.
- **Paramètre** : `event_id` (int)
- **Réponse** :
  - Succès : message de confirmation
  - Échec : `{"detail": "NOT_FOUND"}`
- **Code HTTP** : `200 OK` ou `404 Not Found`

---

### 6. `GET /categories`

- **Description** : Liste toutes les catégories disponibles.
- **Réponse** : liste de catégories au format JSON.
- **Code HTTP** : `200 OK`

---

### 7. `POST /categories`

- **Description** : Crée une nouvelle catégorie.
- **Corps de la requête** : un objet `Category` en JSON.
- **Réponse** : message de confirmation avec l’identifiant.
- **Code HTTP** : `201 Created`

---

## 🧾 Schéma JSON attendu (Event)

```json
{
  "name": "Dentiste",
  "description": "Rendez-vous chez le dentiste",
  "start_dt": "2025-04-01T09:00:00",
  "end_dt": "2025-04-01T10:00:00",
  "rrule": "FREQ=DAILY;COUNT=1",
  "ha_user_id": 1,
  "status": "pending",
  "categories": [
    {
      "id": 1,
      "name": "Santé"
    }
  ]
}
```

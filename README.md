# API DOCUMENTATION

### 1. **Send Otp**

**URL:** `POST /send-otp`  
**Endpoint:** [https://be-budaya-592544960467.asia-southeast2.run.app/send-otp](https://be-budaya-592544960467.asia-southeast2.run.app/send-otp)  
**Request:**

```json
{
    "email": string,
    "full_name": string,
    "password": string
}
```

**Response:**

```json
{
  "message": "OTP telah dikirim ke email"
}
```

---

### 2. **Verify Otp**

**URL:** `POST /verify-otp`  
**Endpoint:** [https://be-budaya-592544960467.asia-southeast2.run.app/verify-otp](https://be-budaya-592544960467.asia-southeast2.run.app/verify-otp)  
**Request:**

```json
{
    "email": string,
    "otp": stirng
}
```

**Response:**

```json
{
  "message": "Akun berhasil dibuat"
}
```

### 3. **login**

**URL:** `POST /login`  
**Endpoint:** [https://be-budaya-592544960467.asia-southeast2.run.app/login](https://be-budaya-592544960467.asia-southeast2.run.app/login)  
**Request:**

```json
{
  tidak ada parameter yang diperlukan
}
```

**Response:**

```json
{
  "results": [
    {
      "label": strign,
      "description": string,
      "image_url": string
    },
    {
      "label": strign,
      "description": string,
      "image_url": string
    }
  ]
}
```

### 4. **Get All Budaya**

**URL:** `GET /getall_budaya`  
**Endpoint:** [https://be-budaya-592544960467.asia-southeast2.run.app/getall_budaya](https://be-budaya-592544960467.asia-southeast2.run.app/getall_budaya)  
**Request:**

```json
{
    "name": string
}
```

**Response:**

```json
{
    "results": [
        {
            "label": string,
            "description": string,
            "image_url": string
        }
        {
            "label": string,
            "description": string,
            "image_url": string
        }
    ]
}
```

### 5. **login**

**URL:** `GET /details`  
**Endpoint:** [https://be-budaya-service-592544960467.asia-southeast2.run.app/details?file_name=[file_name]](https://be-budaya-service-592544960467.asia-southeast2.run.app/details?file_name=[file_name])  
**Request:**

```json
{
    "email": string,
    "password": string
}
```

**Response:**

```json
{
    "message": "Login berhasil",
    "token": string
}
```

---

---

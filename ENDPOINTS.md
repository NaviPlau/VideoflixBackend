# Videoflix API Endpoints

This document provides an overview of the available API endpoints for the Videoflix backend.

For setup and installation, refer to [README.md](README.md).

## Video Endpoints
| Method | Endpoint                              | Description                |
|--------|--------------------------------------|----------------------------|
| POST   | `/videos/upload/`                   | Upload a video (superuser only) |
| GET    | `/videos/`                           | List all videos           |
| GET    | `/videos/<int:video_id>/`           | Get details of a video    |
| GET    | `/video/<int:video_id>/progress/`   | Get video processing status |

## Authentication Endpoints
| Method | Endpoint                                          | Description                 |
|--------|--------------------------------------------------|-----------------------------|
| POST   | `/register/`                                    | Register a new user        |
| GET    | `/activate/<str:uidb64>/<str:token>/`           | Activate user account      |
| POST   | `/reset-password/`                              | Request password reset     |
| POST   | `/reset-password/confirm/<str:token>/`         | Confirm password reset     |
| POST   | `/login/`                                       | User login                 |
| POST   | `/remember-login/`                              | Login via token            |

For further details on request and response formats, refer to the API documentation.


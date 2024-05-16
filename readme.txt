
To test this prototype system you should change the model paths as well as the database credentials :)
Чтобы протестировать эту систему-прототип, вам следует изменить пути к модели, а также учетные данные базы данных :)


dust_detection_project/
│
|___rusal_env/                   # Our virtuale envirement.
|
├── mmyolo/                     # Cloned mmYOLO repository.
│   ├── scripts/                # Scripts for training, validation, testing.
│   └── configs/                # Configuration files for models.
│
├── real_time_detection/        # Custom scripts for real-time detection.
│   ├── stream_processor.py     # Handles multiple RTSP streams using threading.
│   |── database.py             # Manages interactions with the PostgreSQL database.
|   |__ utils.py                # all the functions that we will use in our stream_processor.py.
│
├── trained_models/             # Store trained YOLOv8 models here.
└── best.pt                     # YOLOv8 trained model file
│
├── server/                     # FastAPI server and web interface.
│   ├── main.py                 # FastAPI server script for handling requests and alerts.
│   └── static/                 # Front-end files (HTML/CSS) for the web interface.
│
├── dataset/                    # Dataset for model training and validation.
│   ├── images/                 # Images for training.
│   └── annotations/            # Annotation files.
|
|__ test/                       # folder for testing our model
│   |__videos/                  # all the videos used for testing
|
|__ database_setup/             # Contains scripts for setting up the database.
    ├── setup_database.py       # Script to set up the database and tables
│   └── db_config.json          # Database connection configurations
|
└── requirements.txt            # Python dependencies for the project.

class Subject(db.Model):
    __tablename__ = 'subject'
    # id primary key
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(128), unique=True, nullable=False)
    # color
    color = db.Column(db.String(7), unique=True, nullable=False)
    # code
    code = db.Column(db.String(128), unique=True, nullable=False)
    # users
    users = relationship('User_Subjects', back_populates='subject',
                         order_by='desc(User_Subjects.number)')
    # projects
    projects = relationship('Project', secondary='project_to_subject',
                            back_populates='subjects', lazy='dynamic')

    def __init__(self, name, color):
        self.name = str(name)
        self.color = str(color)
        self.code = str(name).replace('/', '_').replace(' ', '_').lower()
        self.users = []
        self.projects = []

    def __repr__(self):
        return f'<Subject {self.name}>'

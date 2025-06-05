import os 
from flask import Flask, render_template, url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text

path= os.path.abspath(os.path.dirname(__file__))
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+ os.path.join(path, 'transistion.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Fixed spelling
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')


db=SQLAlchemy(app)

class Trans(db.Model):
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    date=db.Column(db.Date, nullable=False)
    amount=db.Column(db.Numeric(10,2), nullable=False)
    type=db.Column(db.String(10), nullable=True)
    category=db.Column(db.String(100),nullable=True)
    description=db.Column(db.String(100))

    def __repr__(self):
        return f'<Trans {self.id}>'

@app.route("/",methods=['GET','POST'])
def index():
    # value=None
    if request.method=="POST":
        date_str = request.form['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        value=Trans(
            date=date_obj,
            amount=request.form['amount'],
            type=request.form['type'],
            category=request.form['category'],
            description=request.form['desc']
        )
        db.session.add(value)
        db.session.commit() 
        return redirect(url_for('index'))
    query=text('''select sum(amount)
               from Trans
               where type="income" ''')
    income=db.session.execute(query).scalar() or 0
    query=text('''select sum(amount)
               from Trans
               where type="expense" ''')
    expanse=db.session.execute(query).scalar() or 0

    return render_template("a.html", v=Trans.query.all(), income=income, expanse=expanse, total=income-expanse)


@app.route('/delete/<int:id>',methods=['GET','POST'])
def delete(id):
    value=Trans.query.get_or_404(id)
    db.session.delete(value)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
    value=Trans.query.get_or_404(id)
    if request.method=="POST":
        value.amount=request.form['amount']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('u.html', value=value)

   

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

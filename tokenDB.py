import secrets
import pymysql

# MySQL 데이터베이스에 연결
conn = pymysql.connect(
    host='host_input',  # 데이터베이스 서버 주소
    user='user_input',  # 데이터베이스 접속 계정
    password='passwd_input',  # 데이터베이스 접속 비밀번호
    db='db_input',  # 사용할 데이터베이스 이름
    charset='utf8mb4'  # 문자 인코딩 설정
)

# 커서 생성
c = conn.cursor()

# 테이블 생성 (이미 존재한다면 넘어감)
c.execute('''
    CREATE TABLE IF NOT EXISTS random_strings_token
    (id INTEGER PRIMARY KEY AUTO_INCREMENT, token VARCHAR(30))
''')

# 20개의 난수를 DB에 저장
for _ in range(20):
    random_string = secrets.token_hex(15)  # 문자와 숫자를 섞어서 30자리의 난수 생성
    c.execute("INSERT INTO random_strings_token (token) VALUES (%s)", (random_string,))

# 변동사항 저장
conn.commit()

# 연결 종료
conn.close()

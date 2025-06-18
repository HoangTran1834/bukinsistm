# Đợi MySQL sẵn sàng
until mysqladmin ping -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" --silent; do
  echo "Waiting for MySQL..."
  sleep 2
done

# Import SQL nếu DB trống
if [ "$(mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e 'SHOW TABLES;' $DB_NAME | wc -l)" -le 1 ]; then
  echo "Importing initial SQL..."
  mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < /app/HeThongDatXe.sql
fi

python manage.py makemigrations datxe_backend
python manage.py migrate
python /scripts/hash_user_password.py
python manage.py runserver 0.0.0.0:8000

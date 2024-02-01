from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)
db_cred = {
    'database': 'database',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'postgres_db',
    'port': '5432'
}


# To avoid connection timeout I will use connect to the db for every query
def connect_db():
    # Connect to db
    conn = psycopg2.connect(**db_cred)

    # Get cursor
    cursor = conn.cursor()
    return conn, cursor


# To avoid connection timeout I will use close the db after every query
def close_db(conn, cursor):
    cursor.close()
    conn.close()


@app.route('/api/countries', methods=['POST'])
def post_country():
    data = request.get_json()
    nume = data.get('nume')
    lat = data.get('lat')
    lon = data.get('lon')

    # Exit if the request is not as it was supposed to be
    if nume is None or lat is None or lon is None:
        return 'BAD REQUEST', 400

    try:
        # Connect to the db
        conn, cursor = connect_db()

        # Execute the query for inserting in 'countries' table
        query = ('INSERT INTO countries (country_name, latitude, longitude) VALUES (%s, %s, %s) '
                 'ON CONFLICT(country_name) DO NOTHING RETURNING id;')
        cursor.execute(query, (nume, lat, lon))
        id_country = cursor.fetchone()[0]
        conn.commit()

        # Close the connection to the db and return
        close_db(conn, cursor)
        return jsonify({"id": id_country}), 201

    # CONFLICT (error 409)
    except Exception as e:
        return str(e), 409


@app.route('/api/countries', methods=['GET'])
def get_countries():
    conn, cursor = connect_db()

    query = 'SELECT * from countries;'
    cursor.execute(query)

    # Get all countries in an array and then format it to json
    res = []
    for country in cursor.fetchall():
        res.append({'id': country[0], 'nume': country[1], 'lat': country[2], 'lon': country[3]})

    close_db(conn, cursor)

    return jsonify(res), 200


@app.route('/api/countries/<int:id_country>', methods=['PUT'])
def put_country(id_country):
    # Get the new data
    data = request.get_json()
    nume = data.get('nume')
    lat = data.get('lat')
    lon = data.get('lon')

    if nume is None or lat is None or lon is None:
        return 'BAD REQUEST', 400

    try:
        conn, cursor = connect_db()

        # Check if the country exists
        query = 'SELECT * from countries WHERE id = %s;'
        cursor.execute(query, (id_country,))
        country = cursor.fetchone()

        # If the country does not exist, return 404
        if country is None:
            close_db(conn, cursor)
            return 'NOT FOUND', 404

        # Update the country
        query = 'UPDATE countries SET country_name = %s, latitude = %s, longitude = %s WHERE id = %s;'
        cursor.execute(query, (nume, lat, lon, id_country))
        conn.commit()

        close_db(conn, cursor)
        return 'OK', 200

    # CONFLICT
    except Exception as e:
        return str(e), 409


@app.route('/api/countries/<int:id_country>', methods=['DELETE'])
def delete_country(id_country):
    conn, cursor = connect_db()

    # Check if the country exists
    query = 'SELECT * from countries WHERE id = %s;'
    cursor.execute(query, (id_country,))
    country = cursor.fetchone()

    # If the country does not exist, return 404
    if country is None:
        close_db(conn, cursor)
        return 'NOT FOUND', 404

    # Delete the country
    query = 'DELETE from countries WHERE id = %s;'
    cursor.execute(query, (id_country,))
    conn.commit()

    close_db(conn, cursor)
    return 'OK', 200


@app.route('/api/cities', methods=['POST'])
def post_city():
    data = request.get_json()
    id_tara = data.get('idTara')
    nume = data.get('nume')
    lat = data.get('lat')
    lon = data.get('lon')

    # Exit if the request is not as it was supposed to be
    if id_tara is None or nume is None or lat is None or lon is None:
        return 'BAD REQUEST', 400

    try:
        # Connect to the db
        conn, cursor = connect_db()

        # Check if country exists
        query = 'SELECT * from countries WHERE id = %s;'
        cursor.execute(query, (id_tara,))
        country = cursor.fetchone()

        if country is None:
            close_db(conn, cursor)
            return 'NOT FOUND', 404

        # Execute the query for inserting in 'countries' table
        query = ('INSERT INTO cities (id_country, city_name, latitude, longitude) VALUES (%s, %s, %s, %s) '
                 'ON CONFLICT(id_country, city_name) DO NOTHING RETURNING id;')
        cursor.execute(query, (id_tara, nume, lat, lon))
        id_city = cursor.fetchone()[0]
        conn.commit()

        # Close the connection to the db and return
        close_db(conn, cursor)
        return jsonify({"id": id_city}), 201

    # CONFLICT
    except Exception as e:
        return str(e), 409


@app.route('/api/cities', methods=['GET'])
def get_cities():
    conn, cursor = connect_db()

    query = 'SELECT * from cities;'
    cursor.execute(query)

    # Get all cities in an array and then return it in json format
    res = []
    for city in cursor.fetchall():
        res.append({'id': city[0], 'idTara': city[1], 'nume': city[2], 'lat': city[3], 'lon': city[4]})

    close_db(conn, cursor)

    return jsonify(res), 200


@app.route('/api/cities/country/<int:id_tara>', methods=['GET'])
def get_cities_country(id_tara):
    conn, cursor = connect_db()

    query = 'SELECT * from cities WHERE id_country = %s;'
    cursor.execute(query, (id_tara,))

    # Get all cities in an array and then return it in json format
    res = []
    for city in cursor.fetchall():
        res.append({'id': city[0], 'idTara': city[1], 'nume': city[2], 'lat': city[3], 'lon': city[4]})

    close_db(conn, cursor)

    return jsonify(res), 200


@app.route('/api/cities/<int:id_city>', methods=['PUT'])
def put_city(id_city):
    data = request.get_json()
    id_tara = data.get('idTara')
    nume = data.get('nume')
    lat = data.get('lat')
    lon = data.get('lon')

    # Exit if the request is not as it was supposed to be
    if id_tara is None or nume is None or lat is None or lon is None:
        return 'BAD REQUEST', 400

    try:
        conn, cursor = connect_db()

        # Check if the city exists
        query = 'SELECT * from cities WHERE id = %s;'
        cursor.execute(query, (id_city,))
        city = cursor.fetchone()

        # If the city does not exist, return 404
        if city is None:
            close_db(conn, cursor)
            return 'NOT FOUND', 404

        # Update city
        query = 'UPDATE cities SET id_country = %s, city_name = %s, latitude = %s, longitude = %s WHERE id = %s;'
        cursor.execute(query, (id_tara, nume, lat, lon, id_city))
        conn.commit()

        close_db(conn, cursor)
        return 'OK', 200

    # CONFLICT
    except Exception as e:
        return str(e), 409


@app.route('/api/cities/<int:id_city>', methods=['DELETE'])
def delete_city(id_city):
    conn, cursor = connect_db()

    # Check if city exists
    query = 'SELECT * from cities WHERE id = %s;'
    cursor.execute(query, (id_city,))
    city = cursor.fetchone()

    # If the city does not exist, return 404
    if city is None:
        close_db(conn, cursor)
        return 'NOT FOUND', 404

    # Delete city
    query = 'DELETE from cities WHERE id = %s;'
    cursor.execute(query, (id_city,))
    conn.commit()

    close_db(conn, cursor)
    return 'OK', 200


@app.route('/api/temperatures', methods=['POST'])
def post_temperature():
    data = request.get_json()
    value = data.get('valoare')
    id_oras = data.get('idOras')

    # Exit if the request is not as it was supposed to be
    if id_oras is None or value is None:
        return 'BAD REQUEST', 400

    try:
        # Connect to the db
        conn, cursor = connect_db()

        # Check if city exists
        query = 'SELECT * from cities WHERE id = %s;'
        cursor.execute(query, (id_oras,))
        city = cursor.fetchone()

        if city is None:
            close_db(conn, cursor)
            return 'NOT FOUND', 404

        # Execute the query for inserting in 'temperatures' table
        query = ('INSERT INTO temperatures (value, id_city) VALUES (%s, %s) '
                 'ON CONFLICT(id_city, timestamp) DO NOTHING RETURNING id;')
        cursor.execute(query, (value, id_oras))
        id_city = cursor.fetchone()[0]
        conn.commit()

        # Close the connection to the db and return
        close_db(conn, cursor)
        return jsonify({"id": id_city}), 201

    # CONFLICT
    except Exception as e:
        return str(e), 409


@app.route('/api/temperatures', methods=['GET'])
def get_temperatures_lat_lon():
    args = request.args
    lat = args.get('lat')
    lon = args.get('lon')
    start_date = args.get('from')
    end_date = args.get('until')

    conn, cursor = connect_db()

    query = 'SELECT t.id, t.value, t.timestamp from temperatures t, cities c WHERE t.id_city = c.id'
    var = []

    # Build query depending on the received arguments
    if lat is not None:
        query += ' and c.latitude = %s'
        var.append(lat)
    if lon is not None:
        query += ' and c.longitude = %s'
        var.append(lon)
    if start_date is not None:
        query += ' and t.timestamp >= %s'
        var.append(start_date)
    if end_date is not None:
        query += ' and t.timestamp <= %s'
        var.append(end_date)

    cursor.execute(query, var)

    # Get all temperatures in an array and return it in json format
    res = []
    for temperature in cursor.fetchall():
        res.append({'id': temperature[0], 'valoare': temperature[1], 'timestamp': temperature[2].strftime('%Y-%m-%d')})

    close_db(conn, cursor)
    return jsonify(res), 200


@app.route('/api/temperatures/cities/<int:id_oras>', methods=['GET'])
def get_temperatures_city(id_oras):
    args = request.args
    start_date = args.get('from')
    end_date = args.get('until')

    conn, cursor = connect_db()

    query = 'SELECT * from temperatures WHERE id_city = %s'
    var = [id_oras]

    # Build query depending on the received arguments
    if start_date is not None:
        query += ' and t.timestamp >= %s'
        var.append(start_date)
    if end_date is not None:
        query += ' and t.timestamp <= %s'
        var.append(end_date)

    cursor.execute(query, var)

    # Get all temperatures in an array and return it in json format
    res = []
    for temperature in cursor.fetchall():
        res.append({'id': temperature[0], 'valoare': temperature[1], 'timestamp': temperature[2].strftime('%Y-%m-%d')})

    close_db(conn, cursor)
    return jsonify(res), 200


@app.route('/api/temperatures/countries/<int:id_tara>', methods=['GET'])
def get_temperatures_country(id_tara):
    args = request.args
    start_date = args.get('from')
    end_date = args.get('until')

    conn, cursor = connect_db()

    query = 'SELECT * from temperatures t, cities c WHERE t.id_city = c.id and c.id_country = %s'
    var = [id_tara]

    # Build query depending on the received arguments
    if start_date is not None:
        query += ' and t.timestamp >= %s'
        var.append(start_date)
    if end_date is not None:
        query += ' and t.timestamp <= %s'
        var.append(end_date)

    cursor.execute(query, var)

    # Get all temperatures in an array and return it in json format
    res = []
    for temperature in cursor.fetchall():
        res.append({'id': temperature[0], 'valoare': temperature[1], 'timestamp': temperature[2].strftime('%Y-%m-%d')})

    close_db(conn, cursor)
    return jsonify(res), 200


@app.route('/api/temperatures/<int:id_temperature>', methods=['PUT'])
def put_temperature(id_temperature):
    data = request.get_json()
    id_temp = data.get('id')
    value = data.get('valoare')
    id_oras = data.get('idOras')

    # Exit if the request is not as it was supposed to be
    if id_temp is None or value is None or id_oras is None:
        return 'BAD REQUEST', 400

    try:
        conn, cursor = connect_db()

        # Check if the city exists
        query = 'SELECT * from temperatures WHERE id = %s;'
        cursor.execute(query, (id_temp,))
        temperature = cursor.fetchone()

        # If the city does not exist, return 404
        if temperature is None:
            close_db(conn, cursor)
            return 'NOT FOUND', 404

        # Update temperature
        query = 'UPDATE temperatures SET value = %s, id_city = %s WHERE id = %s;'
        cursor.execute(query, (value, id_oras, id_temperature))
        conn.commit()

        close_db(conn, cursor)
        return 'OK', 200

    # CONFLICT
    except Exception as e:
        return str(e), 409


@app.route('/api/temperatures/<int:id_temperature>', methods=['DELETE'])
def delete_temperature(id_temperature):
    conn, cursor = connect_db()

    # Check if city exists
    query = 'SELECT * from temperatures WHERE id = %s;'
    cursor.execute(query, (id_temperature,))
    temperature = cursor.fetchone()

    # If the temperature does not exist, return 404
    if temperature is None:
        close_db(conn, cursor)
        return 'NOT FOUND', 404

    # Delete temperature
    query = 'DELETE from temperatures WHERE id = %s;'
    cursor.execute(query, (id_temperature,))
    conn.commit()

    close_db(conn, cursor)
    return 'OK', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

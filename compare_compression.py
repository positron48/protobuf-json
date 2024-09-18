import json
import lz4.frame
from data_pb2 import DataPacket, SimpleRecord, ComplexRecord, LargeRecord

def generate_simple_data(num_records):
    """Генерирует простой пакет данных."""
    return {
        "simple_records": [
            {
                "id": i,
                "name": f"Name{i}"
            }
            for i in range(num_records)
        ]
    }

def generate_complex_data(num_records):
    """Генерирует сложный пакет данных."""
    return {
        "complex_records": [
            {
                "id": i,
                "name": f"Name{i}",
                "description": f"Description of record {i}",
                "value": float(i) * 1.1,
                "isActive": i % 2 == 0,
                "tags": [f"tag{j}" for j in range(5)]
            }
            for i in range(num_records)
        ]
    }

def generate_large_data(num_records):
    """Генерирует пакет данных с большими текстовыми значениями."""
    long_text = "<html>" + ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 10) + "</html>"
    return {
        "large_records": [
            {
                "id": i,
                "title": f"Title {i}",
                "content": long_text
            }
            for i in range(num_records)
        ]
    }

def serialize_json(data):
    """Сериализует данные в JSON."""
    return json.dumps(data).encode('utf-8')

def serialize_protobuf(data):
    """Сериализует данные в Protobuf."""
    packet = DataPacket()
    if 'simple_records' in data:
        for record in data['simple_records']:
            rec = packet.simple_records.add()
            rec.id = record['id']
            rec.name = record['name']
    elif 'complex_records' in data:
        for record in data['complex_records']:
            rec = packet.complex_records.add()
            rec.id = record['id']
            rec.name = record['name']
            rec.description = record['description']
            rec.value = record['value']
            rec.isActive = record['isActive']
            rec.tags.extend(record['tags'])
    elif 'large_records' in data:
        for record in data['large_records']:
            rec = packet.large_records.add()
            rec.id = record['id']
            rec.title = record['title']
            rec.content = record['content']
    return packet.SerializeToString()

def compress_data(data):
    """Компрессия данных с использованием lz4."""
    return lz4.frame.compress(data)

def measure_size(data):
    """Измеряет размер данных в байтах."""
    return len(data)

def compare_compression(generate_data_func, num_records_list, data_type_name):
    results = []
    for num_records in num_records_list:
        data = generate_data_func(num_records)
        
        # Сериализация
        json_data = serialize_json(data)
        protobuf_data = serialize_protobuf(data)
        
        # Компрессия
        json_compressed = compress_data(json_data)
        protobuf_compressed = compress_data(protobuf_data)
        
        # Измерение размеров
        sizes = {
            'data_type': data_type_name,
            'num_records': num_records,
            'json_size': measure_size(json_data),
            'protobuf_size': measure_size(protobuf_data),
            'json_compressed_size': measure_size(json_compressed),
            'protobuf_compressed_size': measure_size(protobuf_compressed)
        }
        
        # Расчет коэффициента компрессии
        sizes['json_compression_ratio'] = sizes['json_size'] / sizes['json_compressed_size']
        sizes['protobuf_compression_ratio'] = sizes['protobuf_size'] / sizes['protobuf_compressed_size']
        
        results.append(sizes)
    return results

# Заданные размеры пакетов
packet_sizes = [1, 10, 100, 1000]

# Сравнение компрессии для простых данных
simple_results = compare_compression(generate_simple_data, packet_sizes, 'Simple')

# Сравнение компрессии для сложных данных
complex_results = compare_compression(generate_complex_data, packet_sizes, 'Complex')

# Сравнение компрессии для больших данных
large_results = compare_compression(generate_large_data, packet_sizes, 'Large')

# Объединение всех результатов
all_results = simple_results + complex_results + large_results

# Вывод результатов
for result in all_results:
    print(f"Тип данных: {result['data_type']}")
    print(f"Количество записей: {result['num_records']}")
    print(f"JSON - Размер: {result['json_size']} байт, Сжатый размер: {result['json_compressed_size']} байт, Коэффициент сжатия: {result['json_compression_ratio']:.2f}")
    print(f"Protobuf - Размер: {result['protobuf_size']} байт, Сжатый размер: {result['protobuf_compressed_size']} байт, Коэффициент сжатия: {result['protobuf_compression_ratio']:.2f}")
    print("-" * 50)

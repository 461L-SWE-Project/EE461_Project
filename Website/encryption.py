
import hashlib
# class encryption:
    
def hash_string(to_hash):
    string = to_hash.encode()
    result = hashlib.sha256(string) #hash value       
    hex_value = result.hexdigest()
    return hex_value
    
    

    

    




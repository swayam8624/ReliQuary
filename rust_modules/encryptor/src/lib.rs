use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use generic_array::{typenum::U32, GenericArray};
use hex;
use pqcrypto_falcon::falcon1024 as falcon;
use pqcrypto_kyber::kyber1024 as kyber;
use pqcrypto_traits::kem::{
    Ciphertext as KemCiphertext, PublicKey as KemPublicKey, SecretKey as KemSecretKey, SharedSecret,
};
use pqcrypto_traits::sign::{
    DetachedSignature, PublicKey as SigPublicKey, SecretKey as SigSecretKey, SignedMessage,
};
use pyo3::prelude::*;
use pyo3::Bound;
// Kyber-1024 constants
const KYBER_PUBLICKEYBYTES: usize = 1568;
const KYBER_SECRETKEYBYTES: usize = 3168;
const KYBER_CIPHERTEXTBYTES: usize = 1568;

// Falcon-1024 constants
const FALCON_PUBLICKEYBYTES: usize = 1793;
const FALCON_SECRETKEYBYTES: usize = 2305;

/// Python module for Reliquary encryption primitives
#[pymodule]
fn reliquary_encryptor(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encrypt_data, m)?)?;
    m.add_function(wrap_pyfunction!(decrypt_data, m)?)?;

    m.add_function(wrap_pyfunction!(encrypt_data_with_nonce, m)?)?;
    m.add_function(wrap_pyfunction!(decrypt_data_with_nonce, m)?)?;

    m.add_function(wrap_pyfunction!(generate_kyber_keys, m)?)?;
    m.add_function(wrap_pyfunction!(encapsulate_kyber, m)?)?;
    m.add_function(wrap_pyfunction!(decapsulate_kyber, m)?)?;

    m.add_function(wrap_pyfunction!(generate_falcon_keys, m)?)?;
    m.add_function(wrap_pyfunction!(sign_falcon, m)?)?;
    m.add_function(wrap_pyfunction!(verify_falcon, m)?)?;
    Ok(())
}

/// Encrypts data using AES-GCM-256. Returns (ciphertext_with_tag, nonce)
#[pyfunction]
fn encrypt_data(data: Vec<u8>, key_bytes: Vec<u8>) -> PyResult<(Vec<u8>, Vec<u8>)> {
    if key_bytes.len() != 32 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Key must be 32 bytes for AES-256",
        ));
    }
    let key = GenericArray::<u8, U32>::from_slice(&key_bytes);
    let cipher = Aes256Gcm::new(key);
    let nonce = Aes256Gcm::generate_nonce(&mut OsRng);

    let ciphertext_with_tag = cipher.encrypt(&nonce, data.as_ref()).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Encryption error: {:?}", e))
    })?;

    Ok((ciphertext_with_tag, nonce.to_vec()))
}

/// Encrypts data with an explicitly provided nonce (for Python FFI)
#[pyfunction]
fn encrypt_data_with_nonce(
    data: Vec<u8>,
    key_bytes: Vec<u8>,
    nonce_bytes: Vec<u8>,
) -> PyResult<Vec<u8>> {
    if key_bytes.len() != 32 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Key must be 32 bytes",
        ));
    }
    if nonce_bytes.len() != 12 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Nonce must be 12 bytes",
        ));
    }

    let key = GenericArray::<u8, U32>::from_slice(&key_bytes);
    let cipher = Aes256Gcm::new(key);
    let nonce = Nonce::from_slice(&nonce_bytes);

    let ciphertext_with_tag = cipher.encrypt(nonce, data.as_ref()).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Encryption error: {:?}", e))
    })?;

    Ok(ciphertext_with_tag)
}

/// Decrypts AES-GCM-256 encrypted data. Returns plaintext or raises ValueError on failure
#[pyfunction]
fn decrypt_data(ciphertext_with_tag: &[u8], nonce: &[u8], key_bytes: &[u8]) -> PyResult<Vec<u8>> {
    if key_bytes.len() != 32 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Key must be 32 bytes",
        ));
    }
    if nonce.len() != 12 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Nonce must be 12 bytes",
        ));
    }

    let key = GenericArray::<u8, U32>::from_slice(key_bytes);
    let cipher = Aes256Gcm::new(key);
    let nonce = Nonce::from_slice(nonce);

    match cipher.decrypt(nonce, ciphertext_with_tag) {
        Ok(plaintext) => Ok(plaintext),
        Err(e) => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Decryption failed: {:?}",
            e
        ))),
    }
}

/// Python-friendly wrapper: Vec inputs/outputs
#[pyfunction]
fn decrypt_data_with_nonce(
    ciphertext_with_tag: Vec<u8>,
    key_bytes: Vec<u8>,
    nonce_bytes: Vec<u8>,
) -> PyResult<Vec<u8>> {
    decrypt_data(&ciphertext_with_tag, &nonce_bytes, &key_bytes)
}

/// Generate Kyber-1024 public/private keypair for post-quantum key encapsulation
#[pyfunction]
fn generate_kyber_keys() -> PyResult<(Vec<u8>, Vec<u8>)> {
    let (pk, sk) = kyber::keypair();
    Ok((pk.as_bytes().to_vec(), sk.as_bytes().to_vec()))
}

/// Kyber-1024 encapsulation - generate shared secret and ciphertext
#[pyfunction]
fn encapsulate_kyber(pk_bytes: Vec<u8>) -> PyResult<(Vec<u8>, Vec<u8>)> {
    if pk_bytes.len() != KYBER_PUBLICKEYBYTES {
        return Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Invalid public key length. Expected {}, got {}",
            KYBER_PUBLICKEYBYTES,
            pk_bytes.len()
        )));
    }

    let pk = kyber::PublicKey::from_bytes(&pk_bytes).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Invalid public key: {:?}", e))
    })?;

    let (ss, ct) = kyber::encapsulate(&pk);
    Ok((ss.as_bytes().to_vec(), ct.as_bytes().to_vec()))
}

/// Kyber-1024 decapsulation - recover shared secret from ciphertext
#[pyfunction]
fn decapsulate_kyber(ct_bytes: Vec<u8>, sk_bytes: Vec<u8>) -> PyResult<Vec<u8>> {
    if ct_bytes.len() != KYBER_CIPHERTEXTBYTES {
        return Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Invalid ciphertext length. Expected {}, got {}",
            KYBER_CIPHERTEXTBYTES,
            ct_bytes.len()
        )));
    }

    if sk_bytes.len() != KYBER_SECRETKEYBYTES {
        return Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Invalid secret key length. Expected {}, got {}",
            KYBER_SECRETKEYBYTES,
            sk_bytes.len()
        )));
    }

    let ct = kyber::Ciphertext::from_bytes(&ct_bytes).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Invalid ciphertext: {:?}", e))
    })?;

    let sk = kyber::SecretKey::from_bytes(&sk_bytes).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Invalid secret key: {:?}", e))
    })?;

    let ss = kyber::decapsulate(&ct, &sk);
    Ok(ss.as_bytes().to_vec())
}

/// Generate Falcon-1024 public/private keypair for post-quantum digital signatures
#[pyfunction]
fn generate_falcon_keys() -> PyResult<(Vec<u8>, Vec<u8>)> {
    let (pk, sk) = falcon::keypair();
    Ok((pk.as_bytes().to_vec(), sk.as_bytes().to_vec()))
}

/// Falcon-1024 signature generation
#[pyfunction]
fn sign_falcon(msg: Vec<u8>, sk_bytes: Vec<u8>) -> PyResult<Vec<u8>> {
    if sk_bytes.len() != FALCON_SECRETKEYBYTES {
        return Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Invalid secret key length. Expected {}, got {}",
            FALCON_SECRETKEYBYTES,
            sk_bytes.len()
        )));
    }

    let sk = falcon::SecretKey::from_bytes(&sk_bytes).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Invalid secret key: {:?}", e))
    })?;

    let signed_msg = falcon::sign(&msg, &sk);
    Ok(signed_msg.as_bytes().to_vec())
}

/// Falcon-1024 signature verification
#[pyfunction]
fn verify_falcon(msg: Vec<u8>, sig_bytes: Vec<u8>, pk_bytes: Vec<u8>) -> PyResult<bool> {
    if pk_bytes.len() != FALCON_PUBLICKEYBYTES {
        return Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Invalid public key length. Expected {}, got {}",
            FALCON_PUBLICKEYBYTES,
            pk_bytes.len()
        )));
    }

    let pk = falcon::PublicKey::from_bytes(&pk_bytes).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Invalid public key: {:?}", e))
    })?;

    let signed_msg = falcon::SignedMessage::from_bytes(&sig_bytes).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Invalid signature: {:?}", e))
    })?;

    match falcon::open(&signed_msg, &pk) {
        Ok(recovered_msg) => Ok(recovered_msg == msg),
        Err(_) => Ok(false),
    }
}

use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use generic_array::{typenum::U32, GenericArray};
use pyo3::prelude::*;
use pyo3::Bound;

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

/// Placeholder Kyber public/private keypair generation
#[pyfunction]
fn generate_kyber_keys() -> PyResult<(Vec<u8>, Vec<u8>)> {
    Ok((vec![1u8; 32], vec![2u8; 32]))
}

/// Placeholder Kyber encapsulation
#[pyfunction]
fn encapsulate_kyber(_pk: Vec<u8>) -> PyResult<(Vec<u8>, Vec<u8>)> {
    Ok((vec![3u8; 32], vec![4u8; 32]))
}

/// Placeholder Kyber decapsulation
#[pyfunction]
fn decapsulate_kyber(_ct: Vec<u8>, _sk: Vec<u8>) -> PyResult<Vec<u8>> {
    Ok(vec![5u8; 32])
}

/// Placeholder Falcon keypair
#[pyfunction]
fn generate_falcon_keys() -> PyResult<(Vec<u8>, Vec<u8>)> {
    Ok((vec![6u8; 32], vec![7u8; 32]))
}

/// Placeholder Falcon signature
#[pyfunction]
fn sign_falcon(_msg: Vec<u8>, _sk: Vec<u8>) -> PyResult<Vec<u8>> {
    Ok(vec![8u8; 64])
}

/// Placeholder Falcon verification
#[pyfunction]
fn verify_falcon(_msg: Vec<u8>, _sig: Vec<u8>, _pk: Vec<u8>) -> PyResult<bool> {
    Ok(true)
}

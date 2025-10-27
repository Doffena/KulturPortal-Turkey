#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel'den okunan verileri işleyen, her 500 kayıtta bir JSON çıktısı üreten,
Google Generative AI ile içerik oluşturan ve detaylı loglama ile hata yönetimi
sunan bir örnek koddur.

Bu versiyon, dört API anahtarıyla limitleri yönetir, 429 hatası alındığında
anahtarı değiştirir veya gerekirse 120 saniye bekler, her 50 istekte bir
anahtarı otomatik olarak günceller ve her 100 başarılı yanıttan sonra 10 saniye
bekleme ekler.
"""

import os
import time
import json
import logging
from typing import List, Dict, Any, Optional

import pandas as pd
import google.generativeai as genai
from google.generativeai.types.generation_types import GenerateContentResponse

# Kullanıcı tarafından belirtilen ek modül:
# QAModelPromt.py içinde tanımlı olan 'PromtAgentV_02' değişkenini kullanıyoruz.
try:
    from QAModelPromt import PromtAgentV_02
except ImportError:
    # Gerçek projede burada uygun bir önlem veya uyarı verilebilir.
    PromtAgentV_02 = (
        """
**Merhaba, bir QA modeli oluşturmak istiyorum.**  
Elimde QA bağlamı oluşturmak için gerekli bilgiler mevcut. Lütfen aşağıdaki adımları takip ederek **SQuAD tarzında 5 adet soru-cevap çifti** oluştur. Bu soru-cevap çiftleri, ilgili bağlam ile **tamamen uyumlu** olacak ve **SQuAD formatında** cevapların başlangıç konumunu (answer start id) da içerecek şekilde hazırlanacaktır.  
Cevap verirken sadece oluşturduğun **SQuAD tarzındaki soruları ve cevapları ver.**

---

### Yöntem ve Adımlar

1. **Bağlamı Derinlemesine Analiz Et**  
   - Verilen bilgileri dikkatlice incele ve bağlamdaki anahtar noktaları belirle.  
   - Bağlamın ana temalarını ve detaylarını anlamak için adım adım analiz yap.  
   - Eğer gerekli görülürse, bağlamdaki her bir kilit bilgiye yönelik mantıksal bir analiz zinciri (Chain of Thought) oluştur.  

2. **Soruları Çeşitlendirerek Tasarla**  
   - Anahtar bilgileri temel alarak, modelin bağlamı daha iyi anlamasını sağlayacak açık, anlaşılır ve çeşitli sorular üret.  
   - Sorular şu şekilde çeşitlendirilebilir:  
     - **Doğrudan bilgi sorgulayan sorular**: Örneğin, bir kavramın açıklanmasını isteyen.  
     - **Neden-sonuç ilişkileri sorgulayan sorular**: Bağlamdaki olaylar ya da bilgiler arasındaki bağlantıyı keşfetmek için.  
     - **Derinlemesine analiz gerektiren sorular**: Detayları ya da karşılaştırmaları incelemek için.

3. **Cevapları Doğruluk ve Netlik Odaklı Üret**  
   - Sorulara bağlamdan türetilmiş net, doğru ve bağlama tamamen uyumlu cevaplar üret.  
   - Cevapların başlangıç konumunu (answer start id) SQuAD formatına uygun şekilde belirt.  

4. **Tutarlılığı Sağlamak İçin Alternatif Yolları Değerlendir**  
   - Her bir soru-cevap çifti için, olası alternatif cevap yollarını göz önünde bulundur.  
   - **Self-Consistency** stratejisi ile en mantıklı ve tutarlı cevabı seç. Bu yöntemde, farklı düşünce yollarını karşılaştırarak en doğru cevabı seçmeye çalış.

5. **Soru-Cevap Çiftlerini Optimize Et ve Sonuçları Değerlendir**  
   - Üretilen tüm soru-cevap çiftlerini dilbilgisi, bağlam uyumu ve açıklık açısından gözden geçir.  
   - **Collaborative and Multi-Agent Approaches** kullanarak, gerekirse her bir çiftin doğruluğunu kontrol etmek için farklı perspektiflerden birden fazla değerlendirme gerçekleştir.  

---

### Örnek Çıktı Formatı

```json
{
  "context": "{ ilgili bağlam burada yer alıyor }",
  "qas": [
    {
      "question": "Buraya bağlama uygun bir soru yazılacak.",
      "answer": {
        "text": "Bağlama uygun cevap burada yer alacak.",
        "answer_start": bağlamdaki_cevabın_başlangıç_konumunu belirten_tam_sayı yer alacak.
      }
    },
    ...
  ]
}
```

"""
    )

# -----------------------------------------------------------------------------
# LOGGING YAPILANDIRMASI
# -----------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    filename="script_log.log",  # Konsolda log görmek isterseniz comment-out yapabilirsiniz.
    filemode="a"
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# API ANAHTARLARI VE İSTEK SAYACI YÖNETİMİ
# -----------------------------------------------------------------------------
API_KEYS = [
    "AIzaSyA7RMv0pw4FCIQQF3pyuNQw8VsFuOyYQvE",
    "AIzaSyAipte5XBC1vwn_1UpjqoHHgCq9PiGzNTo",
    "AIzaSyATxUglZXffcx5ZnyhK7Sqq-ckJ0hueMsk",
    "AIzaSyAwRkl8lsO5_q3bfVkHtwKPCPZRi_Icaas",
]

# Bu değişkenler, sırasıyla anahtar indeksi, o anahtarla yapılan istek sayısı
# ve toplam başarılı yanıt sayısını takip eder.
current_key_index = 0
request_count = 0
success_count = 0


def switch_api_key(force_switch: bool = False) -> str:
    """
    Mevcut API anahtarını döndürür veya gerekirse değiştirir.

    Her bir API anahtarıyla 50 istek yapılabildiği varsayılmakta.
    'force_switch=True' parametresi, 429 vb. hata alındığında zorunlu
    anahtar değiştirmeyi sağlar.

    Args:
        force_switch (bool): Anahtarı zorunlu olarak değiştirmek için kullanılır.

    Returns:
        str: Güncel olarak kullanılacak API anahtarı.
    """
    global API_KEYS, current_key_index, request_count

    if force_switch or request_count >= 50:
        # Anahtarı değiştir
        current_key_index += 1
        request_count = 0  # Sayaç sıfırlanır
        if current_key_index >= len(API_KEYS):
            # Tüm anahtarlar tükenmişse 120 saniye bekleyip başa dön
            logger.warning("All API keys exhausted. Waiting 120 seconds...")
            time.sleep(120)
            current_key_index = 0

    # Güncel anahtarı döndür
    return API_KEYS[current_key_index]


def handle_429_error() -> str:
    """
    429 Too Many Requests hatası alındığında anahtarı değiştirir.
    Eğer tüm anahtarlar tükenmişse 120 saniye bekler ve başa döner.

    Returns:
        str: Yeni API anahtarı.
    """
    global API_KEYS, current_key_index

    # 5 saniye bekle ve anahtarı değiştir
    time.sleep(5)
    logger.warning("Received 429. Switching the API key...")

    current_key_index += 1
    if current_key_index >= len(API_KEYS):
        # Tüm anahtarlar tükenmişse 120 saniye bekleyip başa dön
        logger.error("All API keys used up during 429 error. Waiting 120 seconds...")
        time.sleep(120)
        current_key_index = 0

    return API_KEYS[current_key_index]


def configure_genai(api_key: str) -> None:
    """
    Google Generative AI API'yi verilen anahtarla konfigüre eder.

    Args:
        api_key (str): Google Gemini API anahtarı.
    """
    try:
        genai.configure(api_key=api_key)
        logger.debug(f"Configured Generative AI with API key: {api_key[:6]}***")
    except Exception as err:
        logger.error(f"Error configuring Generative AI: {err}")
        raise


def generate_answer(context_text: str, model: genai.GenerativeModel) -> str:
    """
    Verilen bağlam (context) metnini kullanarak Google Generative AI
    modelinden yanıt üretir.

    Args:
        context_text (str): Modelin bağlam olarak kullanacağı metin.
        model (genai.GenerativeModel): Google Generative AI model örneği.

    Returns:
        str: Model tarafından üretilen yanıt metni.
    """
    global request_count

    # Her yeni istekte sayacı 1 artır
    request_count += 1

    system_instruction = PromtAgentV_02
    generation_config = {
        "temperature": 0.3,
        "max_output_tokens": 2048,
        "top_p": 0.45,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.0,
    }

    prompt = (f"""
    ---
    {system_instruction}
    ---
    **Role: User, Content**:  
    Bağlamı analiz et, soruları oluştur ve cevapları yaz. Soruları SQuAD formatında teslim et.
    "
    Bağlam: {context_text}
    "
    ---
    """)

    while True:
        try:
            response: GenerateContentResponse = model.generate_content(
                contents=[{"role": "user", "parts": [prompt]}],
                generation_config=generation_config
            )
            if not response.candidates:
                logger.warning("No candidate found in response.")
                return ""
            return response.candidates[0].content.parts[0].text

        except Exception as err:
            err_msg = str(err)
            logger.error(f"Error generating answer: {err_msg}")

            # Eğer 429 içeriyorsa (Too Many Requests), anahtar değiştir
            if "429" in err_msg:
                new_key = handle_429_error()
                configure_genai(new_key)
                model = genai.GenerativeModel(new_key)
                continue
            else:
                # Diğer hatalar için tekrar yükseltelim
                raise


def list_available_models() -> Optional[str]:
    """
    Kullanılabilir modelleri listeler ve seçilen modelin adını döndürür.

    Returns:
        Optional[str]: Seçilen modelin adı.
    """
    try:
        available_models = [
            m.name for m in genai.list_models()
            if "generateText" in m.supported_generation_methods
        ]
        logger.debug(f"Available models: {available_models}")

        if not available_models:
            logger.warning("No available models found.")
            return None

        print("Available models:")
        for model_name in available_models:
            print(model_name)

        selected_model = "models/gemini-1.5-flash"
        if selected_model in available_models:
            logger.info(f"Selected model: {selected_model}")
        else:
            logger.warning(
                f"Selected model {selected_model} not found in available models. "
                "Will try to use it anyway."
            )
        return selected_model

    except Exception as exc:
        logger.error(f"Error listing models: {exc}")
        return None


def process_excel_and_generate_answers(
    excel_path: str,
    output_dir: str = "outputs",
    chunk_size: int = 500
) -> None:
    """
    Belirtilen Excel dosyasını okur, her satır için Generative AI modeliyle
    yanıt üretir. Her 500 kayıtta bir JSON dosyası oluşturur. Tüm anahtar, hata
    yönetimi ve bekleme mekanizmalarını entegre eder.

    Args:
        excel_path (str): İşlenecek Excel dosyasının path'i.
        output_dir (str, optional): JSON dosyalarının kaydedileceği klasör adı.
        chunk_size (int, optional): Kaç kayıtta bir JSON dosyası oluşturulacağı.
    """
    global success_count

    # Klasör var mı kontrol et, yoksa oluştur
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.debug(f"Created output directory: {output_dir}")

    # Excel dosyasını oku
    try:
        df = pd.read_excel(excel_path)
        logger.debug(f"Excel file {excel_path} read successfully. Rows: {len(df)}")
    except Exception as exc:
        logger.error(f"Error reading Excel file: {exc}")
        return

    # İlk API anahtarını ve modeli konfigüre et
    initial_key = switch_api_key()
    configure_genai(initial_key)

    model_name = list_available_models()
    if model_name is None:
        logger.error("No model available or error listing models. Exiting...")
        return

    model = genai.GenerativeModel(model_name)

    success_responses: List[Dict[str, Any]] = []
    error_responses: List[Dict[str, Any]] = []
    file_counter = 1  # JSON dosya numaralandırması

    for index, row in df.iterrows():
        context = str(row.get("context", ""))
        row_data = row.to_dict()

        try:
            logger.debug(f"Processing row {index} with context: {context[:50]} ...")
            answer = generate_answer(context, model)

            success_responses.append({
                "row_index": index,
                "row_data": row_data,
                "generated_answer": answer,
            })

            # Her başarılı yanıt için success_count'u 1 artır
            success_count += 1
            logger.info(f"Generated answer for row {index}, total success: {success_count}")

            # Her 100 başarılı yanıttan sonra 10 saniye bekle
            if success_count % 100 == 0:
                logger.info(
                    "Reached 100 successful answers. Waiting 10 seconds..."
                )
                time.sleep(10)

            # 50 istek sonrasında API anahtarını otomatik değiştir
            # switch_api_key() fonksiyonunu generate_answer da çağırıyoruz, ancak
            # orada sadece 429 durumunda çağırılıyor. Bu satırda normal dönüşümlerde
            # anahtarı güncelliyoruz.
            current_key = switch_api_key()
            configure_genai(current_key)
            model = genai.GenerativeModel(model_name)

        except Exception as exc:
            logger.error(f"Error generating answer for row {index}: {exc}")
            error_responses.append({
                "row_index": index,
                "row_data": row_data,
                "error": str(exc)
            })

        # Her chunk_size kadar satır işlendiğinde sonuçları kaydet
        if (index + 1) % chunk_size == 0:
            output_json_path = os.path.join(output_dir, f"output_part_{file_counter}.json")
            try:
                with open(output_json_path, "w", encoding="utf-8") as out_file:
                    json.dump(success_responses, out_file, ensure_ascii=False, indent=4)
                logger.info(f"{chunk_size} responses written to {output_json_path}")
            except Exception as exc:
                logger.error(f"Error writing JSON output: {exc}")

            file_counter += 1
            success_responses = []  # Sıfırla, bir sonraki chunk için hazırla

    # Son kalan başarı ve hata kayıtlarını kaydet
    try:
        # Son kalan başarı kayıtları
        if success_responses:
            output_json_path = os.path.join(output_dir, f"output_part_{file_counter}.json")
            with open(output_json_path, "w", encoding="utf-8") as out_file:
                json.dump(success_responses, out_file, ensure_ascii=False, indent=4)
            logger.info(
                f"Remaining {len(success_responses)} responses written to {output_json_path}"
            )

        # Hatalı kayıtları kaydet
        if error_responses:
            error_json_path = os.path.join(output_dir, "error_responses.json")
            with open(error_json_path, "w", encoding="utf-8") as err_file:
                json.dump(error_responses, err_file, ensure_ascii=False, indent=4)
            logger.warning(f"Error responses written to {error_json_path}")

    except Exception as exc:
        logger.error(f"Error writing remaining responses: {exc}")

    logger.info("All data processing is complete.")


def main():
    """
    Kodun ana çalıştırma fonksiyonu.
    Excel dosyasının yolunu belirler ve işleme başlar.
    """
    excel_file_path = "burak.xlsx"
    process_excel_and_generate_answers(excel_file_path)


if __name__ == "__main__":
    # İsteğe bağlı olarak, belirli zaman aralıklarıyla çalıştırmak için:
    # while True:
    #     main()
    #     time.sleep(3600)  # 1 saat bekle
    main()

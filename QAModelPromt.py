PromtAgentV_02 =""" 

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
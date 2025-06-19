
from flask import Flask, request, jsonify, render_template_string, render_template
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

from database.db import init_db, insert_user, get_user_by_email, get_user_by_token, confirm_user
from utils.telegram_utils import send_telegram_message
from utils.mail_utils import send_confirmation_email
from utils.geo_utils import get_client_ip, get_country_by_ip
from datetime import datetime
import secrets
import re
import os
import requests





app = Flask(__name__)
CORS(app)  # Cross-Origin Request Support
init_db()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@app.route('/')
def home():
    site_key = os.getenv("RECAPTCHA_SITE_KEY")  # ✅ load from .env
    return render_template_string('''

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create ADCPA Account</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f9f9f9;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 40px;
        }

        form {
            background-color: white;
            padding: 30px 40px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
        }

        h2 {
            text-align: center;
            margin-bottom: 25px;
        }

        label {
            font-weight: 500;
            display: block;
            margin-bottom: 10px;
        }

        input, select {
            width: 100%;
            padding: 10px 12px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-sizing: border-box;
            font-size: 14px;
        }

        input:focus, select:focus {
            border-color: #007bff;
            outline: none;
        }

        button {
            width: 100%;
            background-color: #007bff;
            color: white;
            border: none;
            padding: 12px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
        }

        button:hover {
            background-color: #0056b3;
        }

        #msg {
            margin-top: 20px;
            text-align: center;
            color: red;
        }
        @media screen and (max-width: 600px) {
  body {
    padding: 10px;
  }

  form {
    margin: 10px auto;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 0 12px rgba(0,0,0,0.05);
  }

  h2 {
    font-size: 1.3rem;
    margin-bottom: 20px;
  }

  label {
    font-size: 0.95rem;
    margin-bottom: 8px;
  }

  input, select {
    padding: 10px;
    font-size: 1rem;
    margin-bottom: 15px;
  }

  button {
    padding: 12px;
    font-size: 1rem;
    margin-top: 10px;
  }

  #msg {
    font-size: 0.9rem;
  }
}
    </style>
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
</head>
<body>
    <form id="signupForm">
        <h2>Create Your ADCPA Account</h2>

        <label>Email *<input type="email" name="email" required></label>
        
        <style>
  .criteria {
    font-size: 0.85em;
    margin-left: 5px;
    color: red;
  }
  .criteria.valid {
    color: green;
  }
  .toggle-eye {
    cursor: pointer;
    position: absolute;
    top: 50%;
    right: 10px;
    transform: translateY(-50%);
  }
  .input-wrap {
    position: relative;
    margin-bottom: 15px;
  }
</style>

<!-- Password Field -->
<label>Password *</label>
<div class="input-wrap">
<input type="password" id="password" name="password" required>
  <span class="toggle-eye" onclick="toggleVisibility('password')">👁</span>
</div>

<!-- Repeat Password Field -->
<label>Repeat Password *</label>
<div class="input-wrap">
  <input type="password" id="repeat_password" name="repeat_password" required>
  <span class="toggle-eye" onclick="toggleVisibility('repeat_password')">👁</span>
</div>

<!-- Password Criteria -->
<ul id="password-criteria">
  <li id="length" class="criteria">❌ 8 or up to 16 characters</li>
  <li id="case" class="criteria">❌ one uppercase and lowercase</li>
  <li id="digit" class="criteria">❌ one numeric digit</li>
  <li id="special" class="criteria">❌ special character: _-!@#$%^&*()+=[]</li>
  <li id="match" class="criteria">❌ passwords must match</li>
        </ul>
        
        <script>
          const password = document.getElementById("password");
          const repeat = document.getElementById("repeat_password");
        
          const length = document.getElementById("length");
          const caseChar = document.getElementById("case");
          const digit = document.getElementById("digit");
          const special = document.getElementById("special");
          const match = document.getElementById("match");
        
          const specialChars = /[!@#$%^&*()_\-+=👦👦{}|\\:;"'<>,.?/~`]/;
        
          function validate() {
            const val = password.value;
        
            // Length
            if (val.length >= 8 && val.length <= 16) {
              length.classList.add("valid");
              length.textContent = "✅ 8 or up to 16 characters";
            } else {
              length.classList.remove("valid");
              length.textContent = "❌ 8 or up to 16 characters";
            }
        
            // Uppercase and lowercase
            if (/[a-z]/.test(val) && /[A-Z]/.test(val)) {
              caseChar.classList.add("valid");
              caseChar.textContent = "✅ one uppercase and lowercase";
            } else {
              caseChar.classList.remove("valid");
              caseChar.textContent = "❌ one uppercase and lowercase";
            }
        
            // Numeric
            if (/\d/.test(val)) {
              digit.classList.add("valid");
              digit.textContent = "✅ one numeric digit";
            } else {
              digit.classList.remove("valid");
              digit.textContent = "❌ one numeric digit";
            }
        
            // Special characters
            if (specialChars.test(val)) {
              special.classList.add("valid");
              special.textContent = "✅ special character: _-!@#$%^&*()+=[]";
            } else {
              special.classList.remove("valid");
              special.textContent = "❌ special character: _-!@#$%^&*()+=[]";
            }
        
            // Match
            if (val && val === repeat.value) {
              match.classList.add("valid");
              match.textContent = "✅ passwords match";
            } else {
              match.classList.remove("valid");
              match.textContent = "❌ passwords must match";
            }
          }
        
          function toggleVisibility(id) {
            const input = document.getElementById(id);
            input.type = input.type === "password" ? "text" : "password";
          }
        
          password.addEventListener("input", validate);
          repeat.addEventListener("input", validate);
        </script>
        
        <label>First Name *<input type="text" name="first_name" required></label>
        <label>Last Name *<input type="text" name="last_name" required></label>
        <label>Company Name<input type="text" name="company_name"></label>
        <label>Website *<input type="text" name="website" required></label>
        <label>Address and Zipcode *<input type="text" name="address_zipcode" required></label>
        <label>City *<input type="text" name="city" required></label>
        
        <!-- Select2 CSS -->
            <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />

            <!-- Country Dropdown with Flags -->
            <div class="mb-3">
            <label for="country" class="form-label fw-bold" style="font-size: 1.1rem;">
            🌍 Country <span class="text-danger">*</span>
            </label>
            <select id="country" name="country" class="form-select form-select-lg" required style="width: 100%;">
            <option></option> <!-- Placeholder -->
            <!-- A -->
            <option value="AF" data-flag="AF">Afghanistan</option>
            <option value="AL" data-flag="🇦🇱">Albania</option>
            <option value="DZ" data-flag="🇩🇿">Algeria</option>
            <option value="AD" data-flag="🇦🇩">Andorra</option>
            <option value="AO" data-flag="🇦🇴">Angola</option>
            <option value="AG" data-flag="🇦🇬">Antigua and Barbuda</option>
            <option value="AR" data-flag="🇦🇷">Argentina</option>
            <option value="AM" data-flag="🇦🇲">Armenia</option>
            <option value="AU" data-flag="🇦🇺">Australia</option>
            <option value="AT" data-flag="🇦🇹">Austria</option>
            <option value="AZ" data-flag="🇦🇿">Azerbaijan</option>
            
            <!-- B -->
            <option value="BS" data-flag="🇧🇸">Bahamas</option>
            <option value="BH" data-flag="🇧🇭">Bahrain</option>
            <option value="BD" data-flag="🇧🇩">Bangladesh</option>
            <option value="BB" data-flag="🇧🇧">Barbados</option>
            <option value="BY" data-flag="🇧🇾">Belarus</option>
            <option value="BE" data-flag="🇧🇪">Belgium</option>
            <option value="BZ" data-flag="🇧🇿">Belize</option>
            <option value="BJ" data-flag="🇧🇯">Benin</option>
            <option value="BT" data-flag="🇧🇹">Bhutan</option>
            <option value="BO" data-flag="🇧🇴">Bolivia</option>
            <option value="BA" data-flag="🇧🇦">Bosnia and Herzegovina</option>
            <option value="BW" data-flag="🇧🇼">Botswana</option>
            <option value="BR" data-flag="🇧🇷">Brazil</option>
            <option value="BN" data-flag="🇧🇳">Brunei</option>
            <option value="BG" data-flag="🇧🇬">Bulgaria</option>
            <option value="BF" data-flag="🇧🇫">Burkina Faso</option>
            <option value="BI" data-flag="🇧🇮">Burundi</option>
            
            <!-- C -->
            <option value="CV" data-flag="🇨🇻">Cabo Verde</option>
            <option value="KH" data-flag="🇰🇭">Cambodia</option>
            <option value="CM" data-flag="🇨🇲">Cameroon</option>
            <option value="CA" data-flag="🇨🇦">Canada</option>
            <option value="CF" data-flag="🇨🇫">Central African Republic</option>
            <option value="TD" data-flag="🇹🇩">Chad</option>
            <option value="CL" data-flag="🇨🇱">Chile</option>
            <option value="CN" data-flag="🇨🇳">China</option>
            <option value="CO" data-flag="🇨🇴">Colombia</option>
            <option value="KM" data-flag="🇰🇲">Comoros</option>
            <option value="CG" data-flag="🇨🇬">Congo (Brazzaville)</option>
            <option value="CD" data-flag="🇨🇩">Congo (Kinshasa)</option>
            <option value="CR" data-flag="🇨🇷">Costa Rica</option>
            <option value="HR" data-flag="🇭🇷">Croatia</option>
            <option value="CU" data-flag="🇨🇺">Cuba</option>
            <option value="CY" data-flag="🇨🇾">Cyprus</option>
            <option value="CZ" data-flag="🇨🇿">Czech Republic</option>
            
            <!-- D -->
            <option value="DK" data-flag="🇩🇰">Denmark</option>
            <option value="DJ" data-flag="🇩🇯">Djibouti</option>
            <option value="DM" data-flag="🇩🇲">Dominica</option>
            <option value="DO" data-flag="🇩🇴">Dominican Republic</option>
            
            <!-- E -->
            <option value="EC" data-flag="🇪🇨">Ecuador</option>
            <option value="EG" data-flag="🇪🇬">Egypt</option>
            <option value="SV" data-flag="🇸🇻">El Salvador</option>
            <option value="GQ" data-flag="🇬🇶">Equatorial Guinea</option>
            <option value="ER" data-flag="🇪🇷">Eritrea</option>
            <option value="EE" data-flag="🇪🇪">Estonia</option>
            <option value="SZ" data-flag="🇸🇿">Eswatini</option>
            <option value="ET" data-flag="🇪🇹">Ethiopia</option>
            
            <!-- F -->
            <option value="FJ" data-flag="🇫🇯">Fiji</option>
            <option value="FI" data-flag="🇫🇮">Finland</option>
            <option value="FR" data-flag="🇫🇷">France</option>
            
            <!-- G -->
            <option value="GA" data-flag="🇬🇦">Gabon</option>
            <option value="GM" data-flag="🇬🇲">Gambia</option>
            <option value="GE" data-flag="🇬🇪">Georgia</option>
            <option value="DE" data-flag="🇩🇪">Germany</option>
            <option value="GH" data-flag="🇬🇭">Ghana</option>
            <option value="GR" data-flag="🇬🇷">Greece</option>
            <option value="GD" data-flag="🇬🇩">Grenada</option>
            <option value="GT" data-flag="🇬🇹">Guatemala</option>
            <option value="GN" data-flag="🇬🇳">Guinea</option>
            <option value="GW" data-flag="🇬🇼">Guinea-Bissau</option>
            <option value="GY" data-flag="🇬🇾">Guyana</option>
            
            <!-- H -->
            <option value="HT" data-flag="🇭🇹">Haiti</option>
            <option value="HN" data-flag="🇭🇳">Honduras</option>
            <option value="HU" data-flag="🇭🇺">Hungary</option>
            
            <!-- I -->
            <option value="IS" data-flag="🇮🇸">Iceland</option>
            <option value="IN" data-flag="🇮🇳">India</option>
            <option value="ID" data-flag="🇮🇩">Indonesia</option>
            <option value="IR" data-flag="🇮🇷">Iran</option>
            <option value="IQ" data-flag="🇮🇶">Iraq</option>
            <option value="IE" data-flag="🇮🇪">Ireland</option>
            <option value="IL" data-flag="🇮🇱">Israel</option>
            <option value="IT" data-flag="🇮🇹">Italy</option>
            <!-- J -->
            <option value="JM" data-flag="🇯🇲">Jamaica</option>
            <option value="JP" data-flag="🇯🇵">Japan</option>
            <option value="JO" data-flag="🇯🇴">Jordan</option>
            
            <!-- K -->
            <option value="KZ" data-flag="🇰🇿">Kazakhstan</option>
            <option value="KE" data-flag="🇰🇪">Kenya</option>
            <option value="KI" data-flag="🇰🇮">Kiribati</option>
            <option value="KP" data-flag="🇰🇵">Korea, North</option>
            <option value="KR" data-flag="🇰🇷">Korea, South</option>
            <option value="KW" data-flag="🇰🇼">Kuwait</option>
            <option value="KG" data-flag="🇰🇬">Kyrgyzstan</option>
            
            <!-- L -->
            <option value="LA" data-flag="🇱🇦">Laos</option>
            <option value="LV" data-flag="🇱🇻">Latvia</option>
            <option value="LB" data-flag="🇱🇧">Lebanon</option>
            <option value="LS" data-flag="🇱🇸">Lesotho</option>
            <option value="LR" data-flag="🇱🇷">Liberia</option>
            <option value="LY" data-flag="🇱🇾">Libya</option>
            <option value="LI" data-flag="🇱🇮">Liechtenstein</option>
            <option value="LT" data-flag="🇱🇹">Lithuania</option>
            <option value="LU" data-flag="🇱🇺">Luxembourg</option>
            
            <!-- M -->
            <option value="MG" data-flag="🇲🇬">Madagascar</option>
            <option value="MW" data-flag="🇲🇼">Malawi</option>
            <option value="MY" data-flag="🇲🇾">Malaysia</option>
            <option value="MV" data-flag="🇲🇻">Maldives</option>
            <option value="ML" data-flag="🇲🇱">Mali</option>
            <option value="MT" data-flag="🇲🇹">Malta</option>
            <option value="MH" data-flag="🇲🇭">Marshall Islands</option>
            <option value="MR" data-flag="🇲🇷">Mauritania</option>
            <option value="MU" data-flag="🇲🇺">Mauritius</option>
            <option value="MX" data-flag="🇲🇽">Mexico</option>
            <option value="FM" data-flag="🇫🇲">Micronesia</option>
            <option value="MD" data-flag="🇲🇩">Moldova</option>
            <option value="MC" data-flag="🇲🇨">Monaco</option>
            <option value="MN" data-flag="🇲🇳">Mongolia</option>
            <option value="ME" data-flag="🇲🇪">Montenegro</option>
            <option value="MA" data-flag="🇲🇦">Morocco</option>
            <option value="MZ" data-flag="🇲🇿">Mozambique</option>
            <option value="MM" data-flag="🇲🇲">Myanmar</option>
            
            <!-- N -->
            <option value="NA" data-flag="🇳🇦">Namibia</option>
            <option value="NR" data-flag="🇳🇷">Nauru</option>
            <option value="NP" data-flag="🇳🇵">Nepal</option>
            <option value="NL" data-flag="🇳🇱">Netherlands</option>
            <option value="NZ" data-flag="🇳🇿">New Zealand</option>
            <option value="NI" data-flag="🇳🇮">Nicaragua</option>
            <option value="NE" data-flag="🇳🇪">Niger</option>
            <option value="NG" data-flag="🇳🇬">Nigeria</option>
            <option value="MK" data-flag="🇲🇰">North Macedonia</option>
            <option value="NO" data-flag="🇳🇴">Norway</option>
            
            <!-- O -->
            <option value="OM" data-flag="🇴🇲">Oman</option>
            
            <!-- P -->
            <option value="PK" data-flag="🇵🇰">Pakistan</option>
            <option value="PW" data-flag="🇵🇼">Palau</option>
            <option value="PA" data-flag="🇵🇦">Panama</option>
            <option value="PG" data-flag="🇵🇬">Papua New Guinea</option>
            <option value="PY" data-flag="🇵🇾">Paraguay</option>
            <option value="PE" data-flag="🇵🇪">Peru</option>
            <option value="PH" data-flag="🇵🇭">Philippines</option>
            <option value="PL" data-flag="🇵🇱">Poland</option>
            <option value="PT" data-flag="🇵🇹">Portugal</option>
            <!-- Q -->
            <option value="QA" data-flag="🇶🇦">Qatar</option>
            
            <!-- R -->
            <option value="RO" data-flag="🇷🇴">Romania</option>
            <option value="RU" data-flag="🇷🇺">Russia</option>
            <option value="RW" data-flag="🇷🇼">Rwanda</option>
            
            <!-- S -->
            <option value="KN" data-flag="🇰🇳">Saint Kitts and Nevis</option>
            <option value="LC" data-flag="🇱🇨">Saint Lucia</option>
            <option value="VC" data-flag="🇻🇨">Saint Vincent and the Grenadines</option>
            <option value="WS" data-flag="🇼🇸">Samoa</option>
            <option value="SM" data-flag="🇸🇲">San Marino</option>
            <option value="ST" data-flag="🇸🇹">Sao Tome and Principe</option>
            <option value="SA" data-flag="🇸🇦">Saudi Arabia</option>
            <option value="SN" data-flag="🇸🇳">Senegal</option>
            <option value="RS" data-flag="🇷🇸">Serbia</option>
            <option value="SC" data-flag="🇸🇨">Seychelles</option>
            <option value="SL" data-flag="🇸🇱">Sierra Leone</option>
            <option value="SG" data-flag="🇸🇬">Singapore</option>
            <option value="SK" data-flag="🇸🇰">Slovakia</option>
            <option value="SI" data-flag="🇸🇮">Slovenia</option>
            <option value="SB" data-flag="🇸🇧">Solomon Islands</option>
            <option value="SO" data-flag="🇸🇴">Somalia</option>
            <option value="ZA" data-flag="🇿🇦">South Africa</option>
            <option value="SS" data-flag="🇸🇸">South Sudan</option>
            <option value="ES" data-flag="🇪🇸">Spain</option>
            <option value="LK" data-flag="🇱🇰">Sri Lanka</option>
            <option value="SD" data-flag="🇸🇩">Sudan</option>
            <option value="SR" data-flag="🇸🇷">Suriname</option>
            <option value="SE" data-flag="🇸🇪">Sweden</option>
            <option value="CH" data-flag="🇨🇭">Switzerland</option>
            <option value="SY" data-flag="🇸🇾">Syria</option>
            
            <!-- T -->
            <option value="TW" data-flag="🇹🇼">Taiwan</option>
            <option value="TJ" data-flag="🇹🇯">Tajikistan</option>
            <option value="TZ" data-flag="🇹🇿">Tanzania</option>
            <option value="TH" data-flag="🇹🇭">Thailand</option>
            <option value="TL" data-flag="🇹🇱">Timor-Leste</option>
            <option value="TG" data-flag="🇹🇬">Togo</option>
            <option value="TO" data-flag="🇹🇴">Tonga</option>
            <option value="TT" data-flag="🇹🇹">Trinidad and Tobago</option>
            <option value="TN" data-flag="🇹🇳">Tunisia</option>
            <option value="TR" data-flag="🇹🇷">Turkey</option>
            <option value="TM" data-flag="🇹🇲">Turkmenistan</option>
            <option value="TV" data-flag="🇹🇻">Tuvalu</option>
            
            <!-- U -->
            <option value="UG" data-flag="🇺🇬">Uganda</option>
            <option value="UA" data-flag="🇺🇦">Ukraine</option>
            <option value="AE" data-flag="🇦🇪">United Arab Emirates</option>
            <option value="GB" data-flag="🇬🇧">United Kingdom</option>
            <option value="US" data-flag="🇺🇸">United States</option>
            <option value="UY" data-flag="🇺🇾">Uruguay</option>
            <option value="UZ" data-flag="🇺🇿">Uzbekistan</option>
            
            <!-- V -->
            <option value="VU" data-flag="🇻🇺">Vanuatu</option>
            <option value="VA" data-flag="🇻🇦">Vatican City</option>
            <option value="VE" data-flag="🇻🇪">Venezuela</option>
            <option value="VN" data-flag="🇻🇳">Vietnam</option>
            
            <!-- Y -->
            <option value="YE" data-flag="🇾🇪">Yemen</option>
            
            <!-- Z -->
            <option value="ZM" data-flag="🇿🇲">Zambia</option>
            <option value="ZW" data-flag="🇿🇼">Zimbabwe</option>
            </select>
            </div>
        
        <!-- jQuery + Select2 JS -->
        <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
        
        <!-- Activate Select2 with Flag Display -->
        <script>
          function formatCountry(option) {
            if (!option.id) return option.text;
            const flag = $(option.element).data('flag');
            return $(<span>${flag ?? ''} ${option.text}</span>);
          }
        
          $(document).ready(function() {
            $('#country').select2({
              placeholder: "🌍 Select your country",
              allowClear: true,
              templateResult: formatCountry,
              templateSelection: formatCountry,
              width: '100%'
            });
          });
        </script>
            
        <label>Telegram or Messenger *<input type="text" name="messenger" required></label>
        
        <label>Main Verticals *
            <select name="vertical" required>
                <option value="">Select one</option>
                <option value="Dating">Dating</option>
                <option value="Nutra">Nutra</option>
                <option value="App Installs">App Installs</option>
                <option value="Gaming">Gaming</option>
                <option value="Crypto">Crypto</option>
                <option value="E-commerce">E-commerce</option>
            </select>
        </label>
        <label>Monthly Revenue *<input type="text" name="monthly_revenue" required></label>
        <label>Traffic Sources *<input type="text" name="traffic_sources" required></label>
        <div class="g-recaptcha" data-sitekey="{{ site_key }}"></div>
        

        <button type="submit">Signup</button>
        <p id="msg"></p>
    </form>

    <script>
        const form = document.getElementById('signupForm');
        form.onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            let obj = {};
            formData.forEach((value, key) => obj[key] = value);

            if (obj.password !== obj.repeat_password) {
                document.getElementById('msg').textContent = 'Passwords do not match.';
                return;
            }
                // ✅ Add reCAPTCHA response
            obj['g-recaptcha-response'] = grecaptcha.getResponse();
            
            try {
                const res = await fetch('/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(obj)
                });
                const data = await res.json();
                document.getElementById('msg').textContent = data.message || data.error;
                document.getElementById('msg').style.color = data.error ? 'red' : 'green';
            } catch {
                document.getElementById('msg').textContent = 'Network error.';
            }
        };
    </script>
</body>
</html>
    ''', site_key=site_key)



@app.route('/signup', methods=['POST'])
def signup():
    print("Signup route hit")
    print("Request JSON:", request.json)
    data = request.json  # পুরো JSON ডাটা ধরে রাখো
    # ✅ reCAPTCHA check
    recaptcha_response = data.get('g-recaptcha-response')
    if not recaptcha_response:
        return jsonify({"error": "CAPTCHA is required"}), 400

    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY")
    payload = {
        'secret': secret_key,
        'response': recaptcha_response
    }

    recaptcha_result = requests.post(verify_url, data=payload).json()
    if not recaptcha_result.get('success'):
        return jsonify({"error": "CAPTCHA verification failed"}), 400

    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if get_user_by_email(email):
        return jsonify({"message": "Email already used"}), 400
    token = secrets.token_urlsafe(16)
    # আগের মতো insert_user ফাংশনে পুরো data পাঠাও
    insert_user(email, token)

    # ✅ নতুন তথ্য সংগ্রহ
    ip = get_client_ip()
    user_agent = request.headers.get('User-Agent')
    geo = get_country_by_ip(ip)
    signup_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # ✅ আগের কোড হুবহু রেখে, নতুন ইনফো নিচে অ্যাড করা হচ্ছে
    telegram_msg = f"New Signup:\n"
    for key, value in data.items():
        telegram_msg += f"{key}: {value}\n"

    # ✅ নতুন লাইন অ্যাড (সব শেষে)
    telegram_msg += f"\n🌐 IP: {ip}\n"
    telegram_msg += f"🌍 Country: {geo.get('country', 'Unknown')}\n"
    telegram_msg += f"🏙 City: {geo.get('city', 'Unknown')}\n"
    telegram_msg += f"🕒 Signup Time: {signup_time}\n"
    telegram_msg += f"🧭 User-Agent: {user_agent}"

    try:
        send_confirmation_email(email, token)
        send_telegram_message(telegram_msg)  # Telegram message পাঠাও
        return jsonify({"message": "Confirmation email sent. Please check your inbox."})
    except Exception as e:
        print(f"Send email failed: {e}")
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500


@app.route('/confirm/<token>', methods=['GET'])
def confirm(token):
    print(f"🔍 Received token: {token}")
    user = get_user_by_token(token)
    if not user:
        print("❌ Token invalid or expired")
        return "Invalid or expired token.", 400

    print(f"🔎 Found user: {user}")

    if user[3]:  # confirmed ফিল্ড চেক (user[3] মানে confirmed কলাম)
        print("⚠ Already confirmed")
        return "Email already confirmed."

    confirm_user(token)
    print("✅ User confirmed in DB")

    # Telegram-এ নিশ্চিতকরণ মেসেজ পাঠাও
    send_telegram_message(f"✅ Email confirmed: {user[1]}")  # user[1] = email

    print("📤 Telegram message sent request")

    return render_template("confirmation.html")


if __name__ == '__main__':
    app.run(debug=True)

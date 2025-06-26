# HỆ THỐNG ĐẶT XE - LOG PHÁT TRIỂN

## HOÀN THÀNH: Authentication System Refactor (Final Update)

### Ngày: 26/6/2025  
### Task: Hoàn thiện Authentication với OTP + Manual Token Check

#### Các cải tiến cuối cùng:

**1. Simplified Serializers:**
- ❌ Bỏ field `vaitro` khỏi `SignupSerializer` (DB tự handle default)
- ✅ Thêm field `email` optional 
- ✅ `OTPVerifySerializer` chỉ có `sodienthoai` + `otp` (tối giản)
- ✅ `ResetPasswordSerializer` có cả `sodienthoai` + `password`

**2. Manual Staff Detection:**
- ✅ `is_staff_user(request)` parse Authorization header manual
- ✅ Kiểm tra token hợp lệ và `vaitro_id` in [0, 2]
- ✅ Return `False` cho mọi trường hợp khác (không có token, invalid, không phải staff)

**3. Unified Flow Logic:**
- 🔐 **Staff có token**: Tạo tài khoản trực tiếp
- 📱 **User thường/không token**: Gửi OTP
- ✅ **Reset password**: 1 bước (nhập password + phone → gửi OTP → verify chỉ cần OTP)

**4. Schema Updates:**
- ✅ Signup examples bỏ field `vaitro`
- ✅ Reset password hiển thị cả `sodienthoai` + `password`
- ✅ Verify chỉ hiển thị `sodienthoai` + `otp`

**5. Middleware Improvements:**
- ✅ Exempt paths bao gồm tất cả auth endpoints
- ✅ Không chặn endpoint public khi có token
- ✅ Logout response status 200 thay vì 205

#### API Endpoints Final:

1. **`POST /auth/signup/`**
   - Staff + token: Tạo trực tiếp
   - User thường: Lưu data + gửi OTP

2. **`POST /auth/login/`**
   - Có password: Login truyền thống
   - Không password: Gửi OTP

3. **`POST /auth/reset_pw/`**
   - Input: `{sodienthoai, password}`
   - Lưu password + gửi OTP

4. **`POST /auth/verify/`**
   - Input: `{sodienthoai, otp}`
   - Auto-detect action → kích hoạt data

5. **`POST /auth/logout/`**
   - Blacklist cả access + refresh token
   - Return 200 với message

#### Tech Stack:
- **SMS OTP**: Lưu full request data với OTP
- **Token**: Manual parsing cho staff detection
- **Middleware**: Linh hoạt với exempt endpoints
- **Serializers**: Tối giản, chỉ field cần thiết
- **Schemas**: OpenAPI docs chính xác

---

## TODO: USER MANAGEMENT SYSTEM
- [ ] User profile endpoints
- [ ] User role management  
- [ ] User search and filtering
- [ ] User status management

---

## HOÀN THÀNH: Cải thiện Authentication Middleware (Latest)

### Ngày: 26/6/2025  
### Task: Refactor SMS OTP để lưu request data cùng OTP

#### Approach mới: **OTP + Request Data Storage**

Thay vì lưu OTP riêng biệt, giờ lưu **OTP cùng với toàn bộ request data** của user:

```json
// Cache storage format:
{
  "otp": "123456",
  "action_type": "signup", 
  "request_data": {
    "hoten": "Nguyen Van A",
    "email": "a@gmail.com",
    "password": "hashed_password",
    "vaitro": 3
  }
}
```

#### API Flow mới:

1. **`POST /auth/signup/`**
   - Staff: Tạo trực tiếp (không đổi)
   - User: Lưu **toàn bộ request data** + gửi OTP

2. **`POST /auth/login/`**
   - Password: Login trực tiếp (không đổi)  
   - SMS: Lưu phone + gửi OTP

3. **`POST /auth/reset_pw/`**
   - Lưu phone + gửi OTP

4. **`POST /auth/verify/`** - **Single Universal Endpoint**
   - Input: `{sodienthoai, otp, password?, hoten?, email?}`
   - Logic: Verify OTP → detect action_type → kích hoạt data
   - Output: Tùy action (create user, login, reset password)

#### Lợi ích:

✅ **Đơn giản hơn**: 1 verify endpoint cho mọi flow
✅ **Bảo mật hơn**: Request data được mã hóa trong cache  
✅ **Atomic**: Data chỉ được tạo sau khi verify thành công
✅ **User-friendly**: User chỉ cần nhập OTP, hệ thống tự biết làm gì
✅ **Maintainable**: Không cần phân biệt OTP type

#### Files đã refactor:
- `auth/sms_service.py` - Lưu request_data cùng OTP
- `auth/views.py` - Đơn giản hóa verify endpoint
- `auth/schema.py` - Cập nhật documentation
- `note` - Cập nhật log

#### Technical Details:
- **Cache key**: `pending_request:{phone}` (1 request per phone)
- **Auto-detect**: verify_otp() trả về action_type + request_data
- **Fallback**: Verify request có thể override saved data
- **Security**: Request data encrypted trong cache

---

## TODO ITEMS:
- [ ] Test các endpoints
- [ ] Update frontend flows
- [ ] Setup production SMS service

#### Files đã tạo/sửa đổi:

1. **`datxe_backend/auth/sms_config.py`** (MỚI)
   - Tất cả cấu hình SMS OTP
   - Error messages tiếng Việt
   - Cài đặt bảo mật (rate limiting, attempts, blocks)

2. **`datxe_backend/auth/sms_service.py`** (MỚI)
   - Utility class SMSOTPService
   - Generate, send, verify OTP
   - Rate limiting và blocking logic
   - Cache management

3. **`datxe_backend/auth/serializers.py`** (CẬP NHẬT)
   - StaffCreateAccountSerializer (staff tạo account)
   - SMSSignupRequestSerializer (request OTP signup)
   - SMSSignupVerifySerializer (verify OTP signup)
   - SMSLoginRequestSerializer (request OTP login)
   - SMSLoginVerifySerializer (verify OTP login)

4. **`datxe_backend/auth/schema.py`** (CẬP NHẬT)
   - Schema functions cho tất cả endpoints mới
   - OpenAPI documentation
   - Request/response examples

5. **`datxe_backend/auth/views.py`** (CẬP NHẬT)
   - AuthViewSet với các endpoints mới:
     - `/auth/signup_sms_request/` - Request OTP cho đăng ký
     - `/auth/signup_sms_verify/` - Verify OTP và tạo account
     - `/auth/login_sms_request/` - Request OTP cho đăng nhập
     - `/auth/login_sms_verify/` - Verify OTP và đăng nhập
     - `/auth/staff_create/` - Staff tạo account (cần authentication)
   - IsStaffPermission helper class
   - Error handling và response format nhất quán

6. **`API_CHANGES_SMS_OTP.md`** (MỚI)
   - Documentation chi tiết cho frontend team
   - Tất cả endpoints, request/response format
   - Error messages và handling
   - Security notes và best practices
   - Testing guidelines

#### Tính năng chính:

1. **SMS OTP Registration Flow:**
   - POST `/auth/signup_sms_request/` → Request OTP
   - POST `/auth/signup_sms_verify/` → Verify OTP + tạo user + return tokens

2. **SMS OTP Login Flow:**
   - POST `/auth/login_sms_request/` → Request OTP
   - POST `/auth/login_sms_verify/` → Verify OTP + return tokens

3. **Staff Account Creation:**
   - POST `/auth/staff_create/` → Staff tạo account (no SMS needed)

4. **Rate Limiting & Security:**
   - Max 10 OTP requests/day per phone
   - Max 3 failed attempts → block 30 minutes
   - Resend cooldown 60 seconds
   - Daily limit exceeded → block 24 hours

5. **Cache Management:**
   - OTP data: `otp_{phone}_{purpose}`
   - Failed attempts: `otp_attempts_{phone}`
   - Daily requests: `otp_requests_{phone}`
   - Blocked phones: `otp_blocked_{phone}`
   - Resend cooldown: `otp_resend_{phone}_{purpose}`

#### Existing endpoints vẫn hoạt động:
- `/auth/login/` - Traditional password login
- `/auth/register/` - Traditional password registration
- `/auth/logout/`
- `/auth/refresh/`
- `/auth/reset_pw/`

#### Cần làm tiếp theo:
1. **Testing:**
   - Test tất cả endpoints mới
   - Test rate limiting và blocking
   - Test error cases

2. **Frontend Integration:**
   - Cập nhật FE để sử dụng endpoints mới
   - Implement SMS OTP flows
   - Handle tất cả error messages
   - Add countdown timers cho cooldowns

3. **Production Setup:**
   - Configure SMS service thật (nếu cần)
   - Setup Django cache properly
   - Test performance với real load

4. **Optional Enhancements:**
   - Resend OTP endpoint
   - Admin interface cho monitoring
   - Multi-language support

#### Notes:
- Modular architecture - dễ maintain và extend
- Backwards compatible - không ảnh hưởng existing code
- Security-first approach với rate limiting và blocking
- Clear documentation cho frontend team
- Vietnamese error messages cho UX tốt hơn

---

## TODO ITEMS:
- [ ] Test SMS OTP endpoints
- [ ] Update frontend authentication flows
- [ ] Setup production SMS service
- [ ] Add monitoring/analytics
- [ ] Consider adding resend OTP endpoint

---

## CSDL UPDATES (Database Changes Tracking)

### Ngày: 27/6/2025
#### Thay đổi: Thêm trường Thứ tự đón/trả cho DatXe và ChiTietDatXe

**Các trường đã thêm:**
1. **Bảng `DatXe`:**
   - `thuTuDon` INT NULL - Thứ tự đón khách (optional)
   - `thuTuTra` INT NULL - Thứ tự trả khách (optional)

2. **Bảng `ChiTietDatXe`:**
   - `thuTuDon` INT NULL - Thứ tự đón khách (optional) 
   - `thuTuTra` INT NULL - Thứ tự trả khách (optional)

3. **Models Django được cập nhật:**
   - `Datxe.thutudon` 
   - `Datxe.thututra`
   - `Chitietdatxe.thutudon`
   - `Chitietdatxe.thututra`

**Mục đích:** Hỗ trợ quản lý lộ trình đón/trả khách theo thứ tự, giúp tài xế biết được thứ tự di chuyển.

#### Thay đổi trước đó:
1. **Soft Delete cho Ca (26/6/2025):**
   - Thêm `daXoa` BOOLEAN DEFAULT 0 vào bảng `Ca`
   - Cập nhật model `Ca.daxoa`

2. **ON DELETE CASCADE (26/6/2025):**
   - `DatXe` → `DanhGia`: ON DELETE CASCADE
   - `DatXe` → `ChiTietDatXe`: ON DELETE CASCADE  
   - `Ca` → `ChiTietCa`: ON DELETE CASCADE

---

## TODO ITEMS:

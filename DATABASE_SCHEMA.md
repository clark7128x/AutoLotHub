# Схема бази даних та управління доступом (RBAC)

Проєкт використовує реляційну базу даних PostgreSQL. Нижче наведено опис ключових таблиць та механізмів безпеки (B2B модель).

## Таблиці

### 1. `users` (Користувачі)
| Поле | Тип | Опис |
| :--- | :--- | :--- |
| `id` | UUID | Первинний ключ |
| `email` | VARCHAR(255) | Унікальний email (логін) |
| `hashed_password` | VARCHAR(255) | Пароль |
| `first_name` | VARCHAR(100) | Ім'я (менеджер бачить ім'я дилера) |
| `last_name` | VARCHAR(100) | Прізвище |
| `is_active` | BOOLEAN | Статус аккаунта |
| `created_at` | TIMESTAMP | Час створення запису |
| `updated_at` | TIMESTAMP | Час останнього оновлення |

### 2. `roles` & `permissions` (RBAC)
*   **roles:** `id`, `name` (Admin, Manager, Dealer), `description`, `created_at`, `updated_at`
*   **permissions:** `id`, `name`, `resource`, `action`, `created_at`, `updated_at`
*   **user_roles** та **role_permissions:** M:N таблиці зв'язків.

### 3. `car_lots` (Автомобільні лоти)
| Поле | Тип | Опис |
| :--- | :--- | :--- |
| `id` | UUID | Первинний ключ |
| `vin` | VARCHAR(17) | Унікальний VIN-код |
| `make` / `model` / `year` | VARCHAR / SMALLINT | Базові характеристики |
| `price` | NUMERIC(10,2) | Ціна |
| `status` | ENUM | AVAILABLE, RESERVED, SOLD |
| `created_at` | TIMESTAMP | Час створення лоту |
| `updated_at` | TIMESTAMP | Час останнього оновлення |

### 4. `orders` (Замовлення)
Зв'язує `User` (Дилера) та `CarLot`. Одне авто може мати лише одне активне замовлення.
| Поле | Тип | Опис |
| :--- | :--- | :--- |
| `id` | UUID | Первинний ключ |
| `car_lot_id` | UUID | Зв'язок з лотом (UNIQUE constraint) |
| `dealer_id` | UUID | Зв'язок з дилером (NOT NULL) |
| `status` | ENUM | PENDING, CONFIRMED, CANCELLED, DELIVERED |
| `notes` | TEXT | Додаткова інформація (опціонально) |
| `created_at` | TIMESTAMP | Час створення замовлення |
| `updated_at` | TIMESTAMP | Час останнього оновлення |

*Примітка щодо статусів замовлень: скасування (`CANCELLED`) дозволене лише зі статусів `PENDING` і `CONFIRMED`. Замовлення зі статусом `DELIVERED` скасувати не можна.*

## Ізоляція даних (Data Scoping)
Доступ до таблиці `orders` жорстко контролюється на рівні репозиторію. 
*   **Менеджери та Адміни** бачать усю таблицю угод.
*   **Дилери** завжди отримують прихований SQL-фільтр: `WHERE dealer_id = :id`. Це гарантує B2B безпеку: жоден дилер не побачить активність іншого.

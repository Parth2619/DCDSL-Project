# 🎨 How to Perform UPDATE Operations on the UI

## 📍 Location: Cities Management Page
**URL:** `http://127.0.0.1:5000/cities`

---

## 🔄 UPDATE Operation: Update City AQI

### Step-by-Step Guide:

### 1️⃣ **Navigate to Cities Page**
- Click on **"Cities"** in the navigation bar
- You'll see a table with all cities

### 2️⃣ **Find the Update AQI Button**
- Look at the **Actions** column (rightmost column)
- Each city row has a **yellow "AQI" button** 🟡
- Button looks like: `🌥️ AQI`

### 3️⃣ **Click the AQI Button**
- Click on the yellow **"AQI"** button for the city you want to update
- A modal popup will appear: **"Update AQI Values"**

### 4️⃣ **Fill in the Form**

**Required Fields (marked with *):**
- ✅ **AQI Value:** Enter value between 0-500
  - Example: `250`
- ✅ **Date:** Select date using date picker
  - Example: `2024-11-04`

**Optional Pollutant Fields:**
- 🔹 **PM2.5:** Range 0-1000 µg/m³
  - Example: `75.5`
- 🔹 **PM10:** Range 0-2000 µg/m³
  - Example: `150.2`
- 🔹 **NO₂:** Range 0-500 µg/m³
  - Example: `45.3`
- 🔹 **SO₂:** Range 0-500 µg/m³
  - Example: `12.8`
- 🔹 **CO:** Range 0-100 mg/m³
  - Example: `2.5`
- 🔹 **O₃:** Range 0-500 µg/m³
  - Example: `85.0`

### 5️⃣ **Submit the Form**
- Click the yellow **"Update AQI"** button at bottom of modal
- If successful: ✅ Green success message appears
- If error: ❌ Red error message shows what went wrong

---

## 🎯 Visual UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Cities Management                    [+ Add New City]      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 Average AQI by City (Chart)                             │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  📋 All Cities                                              │
│                                                              │
│  ┌────────┬──────────┬─────────┬────────┬─────────────┐   │
│  │ City ID│ City Name│ Pin Code│ State  │   Actions   │   │
│  ├────────┼──────────┼─────────┼────────┼─────────────┤   │
│  │   1    │ Mumbai   │ 400001  │ MH     │ [🌥️ AQI] [🗑️]│   │
│  │   2    │ Delhi    │ 110001  │ DL     │ [🌥️ AQI] [🗑️]│   │
│  │   3    │ Bangalore│ 560001  │ KA     │ [🌥️ AQI] [🗑️]│   │
│  └────────┴──────────┴─────────┴────────┴─────────────┘   │
│              👆 Click the Yellow "AQI" Button               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Modal Popup Form

When you click the **AQI** button, you'll see:

```
┌───────────────────────────────────────────────┐
│  🌥️ Update AQI Values                    [X] │
├───────────────────────────────────────────────┤
│                                               │
│  City: Mumbai                                 │
│                                               │
│  📅 AQI Value *    [ 250    ]                │
│                    Range: 0-500               │
│                                               │
│  📅 Date *         [ 2024-11-04 ]            │
│                                               │
│  ── Pollutant Levels (µg/m³) ──              │
│                                               │
│  PM2.5            [ 75.5    ]                │
│  PM10             [ 150.2   ]                │
│                                               │
│  NO₂              [ 45.3    ]                │
│  SO₂              [ 12.8    ]                │
│                                               │
│  CO               [ 2.5     ]                │
│  O₃               [ 85.0    ]                │
│                                               │
├───────────────────────────────────────────────┤
│         [Cancel]        [Update AQI]          │
└───────────────────────────────────────────────┘
```

---

## ✅ Success Messages

After clicking **Update AQI**, you'll see one of:

### ✅ **Success:**
```
✅ AQI values for "Mumbai" on 2024-11-04 updated successfully! (AQI: 250)
```

### ❌ **Validation Errors:**
```
❌ AQI value must be between 0 and 500!
❌ PM2.5 value (1500 µg/m³) is unrealistic! Valid range: 0-1000 µg/m³
❌ Date cannot be more than 1 year in the future!
❌ City with ID 999 does not exist!
```

---

## 🔐 Important Notes

### 1. **Admin Access Required**
- Only users with **admin** role can see the UPDATE buttons
- If you're logged in as regular user, you won't see the Actions column

### 2. **Smart Update Logic**
- If AQI data already exists for that city and date → **Updates** the record
- If AQI data doesn't exist → **Inserts** new record
- You don't need to worry about this; the system handles it automatically!

### 3. **Validation Checks**
The system validates:
- ✅ Required fields (AQI value, date)
- ✅ AQI range (0-500)
- ✅ Pollutant realistic ranges
- ✅ Date format (YYYY-MM-DD)
- ✅ Date range (not too far in past/future)
- ✅ City existence

---

## 🎬 Quick Demo Workflow

```
1. Login as Admin
   ↓
2. Click "Cities" in navbar
   ↓
3. Find city in table (e.g., "Mumbai")
   ↓
4. Click yellow "AQI" button
   ↓
5. Fill in form:
   - AQI Value: 250
   - Date: Today's date (auto-filled)
   - PM2.5: 75.5 (optional)
   - PM10: 150.2 (optional)
   ↓
6. Click "Update AQI"
   ↓
7. See success message!
   ↓
8. Data is saved in database ✅
```

---

## 🖱️ Other UPDATE Operations

### Update Profile
1. Click **"Profile"** in navbar
2. Edit: Name, Email, City
3. Click **"Update Profile"**

### Update Station (if visible)
1. Navigate to **Stations** page
2. Click **Edit** button for station
3. Modify station details
4. Click **Save**

---

## 🛠️ Testing Your UPDATE Operation

### Try This:
1. Go to: `http://127.0.0.1:5000/cities`
2. Click the **yellow AQI button** on any city
3. Enter these test values:
   ```
   AQI Value: 150
   Date: 2024-11-04
   PM2.5: 55.5
   PM10: 95.0
   NO2: 35.0
   ```
4. Click **Update AQI**
5. You should see: ✅ Success message
6. Check the database:
   ```sql
   SELECT * FROM pollutants WHERE city_id = 1 AND date = '2024-11-04';
   SELECT * FROM aqi WHERE city_id = 1 AND date = '2024-11-04';
   ```

---

## 🐛 Troubleshooting

### "I don't see the AQI button"
- ✅ Make sure you're logged in as **admin**
- ✅ Check the **Actions** column (last column of table)
- ✅ Regular users cannot see this button

### "Modal won't open"
- ✅ Check browser console (F12) for JavaScript errors
- ✅ Make sure jQuery and Bootstrap are loaded
- ✅ Hard refresh page (Ctrl+Shift+R)

### "Getting validation errors"
- ✅ Check AQI value is between 0-500
- ✅ Check date format is YYYY-MM-DD
- ✅ Check pollutant values are realistic
- ✅ Make sure city exists in database

---

## 📸 Screenshots Location

The actual buttons look like:
- **Yellow AQI Button:** `🌥️ AQI` (btn-warning class)
- **Red Delete Button:** `🗑️` (btn-danger class)

The modal has:
- **Orange header** with cloud icon
- **White body** with form fields
- **Yellow "Update AQI" button** at bottom

---

## 🎯 Summary

**To UPDATE City AQI on UI:**
1. Go to Cities page
2. Find city in table
3. Click yellow **"AQI"** button
4. Fill form with AQI value and date
5. Optionally add pollutant values
6. Click **"Update AQI"**
7. See success/error message

**That's it!** The system handles all the validation, database updates, and audit logging automatically. 🚀

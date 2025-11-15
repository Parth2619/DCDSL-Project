// File: backend/middleware/auth.js
export const authenticateAdmin = (req, res, next) => {
  const token = req.headers['x-admin-token'];
  
  if (!token || token !== process.env.ADMIN_TOKEN) {
    return res.status(403).json({ 
      success: false, 
      message: 'Forbidden: Invalid or missing admin token' 
    });
  }
  
  next();
};

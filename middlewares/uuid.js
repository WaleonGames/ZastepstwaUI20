const crypto = require("crypto");

module.exports = function (req, res, next) {
  let uuid = req.cookies.school_uuid;

  if (!uuid) {
    uuid = crypto.randomUUID();
    res.cookie("school_uuid", uuid, {
      httpOnly: true,
      sameSite: "strict",
      secure: false,
      maxAge: 365 * 24 * 60 * 60 * 1000
    });
    console.log("🆕 Utworzono school_uuid:", uuid);
  }

  res.locals.school_uuid = uuid;
  next();
};

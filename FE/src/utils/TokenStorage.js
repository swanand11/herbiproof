export const getToken = () => localStorage.getItem("jwt");
export const setToken = (token) => localStorage.setItem("jwt", token);
export const removeToken = () => localStorage.removeItem("jwt");
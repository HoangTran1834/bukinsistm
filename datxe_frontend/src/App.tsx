import { Outlet } from "react-router-dom";
import "./App.css";
import Footer from "./components/Layout/Footer";

const App = () => {
  return (
    <>
      {/* <Navbar /> */}
      <Outlet />
      <Footer />
    </>
  );
};

export default App;

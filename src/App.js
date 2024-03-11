import logo from './logo.svg';
import './App.css';
import {app} from './firebaseConfig';
import {GithubAuthProvider,getAuth,signInWithPopup} from 'firebase/auth'
function App() {
  const githubProvider=new GithubAuthProvider();
  const auth= getAuth();
  const githubSignUp= () => {
    signInWithPopup(auth,githubProvider)
    .then((response) => {
      console.log(response.user)
    })
    .catch((err) => {
      console.log(err.code)
    })
  }
  return (
    <div className="auth-container">
      <button onClick={githubSignUp}> Github</button>
    </div>
  );
}

export default App;

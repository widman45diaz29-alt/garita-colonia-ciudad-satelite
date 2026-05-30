export default function Mensaje({texto,tipo='exito'}){if(!texto)return null;return <div className={`mensaje ${tipo}`}>{texto}</div>}

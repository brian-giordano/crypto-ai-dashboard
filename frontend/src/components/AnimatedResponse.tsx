import React, { useState, useEffect } from "react";

interface AnimatedResponseProps {
  text: string;
}

const AnimatedResponse: React.FC<AnimatedResponseProps> = ({ text }) => {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    let index = 0;
    const words = text.split(" ");
    const interval = setInterval(() => {
      if (index < words.length) {
        setDisplayedText((prev) => prev + " " + words[index]);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 50); // speed adjustment per word
    return () => clearInterval(interval);
  }, [text]);

  return <>{displayedText}</>;
};

export default AnimatedResponse;

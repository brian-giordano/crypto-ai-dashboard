import React, { useState, useEffect } from "react";

interface AnimatedResponseProps {
  text: string;
}

const AnimatedResponse: React.FC<AnimatedResponseProps> = ({ text }) => {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    if (!text) return; // Early return if text is undefined or empty

    let index = 0;
    const words = text.split(" ").filter((word) => word.trim() !== ""); // Filter out empty strings

    const interval = setInterval(() => {
      if (index < words.length) {
        // Only append if the word is defined
        const nextWord = words[index];
        if (nextWord) {
          setDisplayedText((prev) => prev + (prev ? " " : "") + nextWord);
        }
        index++;
      } else {
        clearInterval(interval); // Stop the interval when all words are processed
      }
    }, 50); // Adjust speed per word

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, [text]);

  console.log("Final displayedText:", displayedText); // Log the final displayed text

  return <>{displayedText}</>;
};

export default AnimatedResponse;

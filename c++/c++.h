extern int debuglog;

struct margins
{
	int	left;
	int	right;
	int top;
	int bottom;

	margins()
	{
		left = right = top = bottom = 0;
	}

	int width()		const	{ return left + right; }
	int height()	const	{ return top + bottom; }
};

namespace ABC {
    enum Numbers {
        One,
        Two,
        Three
    };
    struct S1{
        int a;
        float b;
    };
    class Demo {
    private:
    public:
        int i1;
    public:
        Demo();
        Demo(char i1);
        Demo(int i1, int i2);
        int cproc(
            char c1, unsigned char c2,
            short s1, unsigned short s2,
            int i1, unsigned int i2,
            long l1, unsigned long l2,
            char *cp1
        );
    };
}

extern int endvar;
